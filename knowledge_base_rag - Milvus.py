# 1. Import required modules
from pathlib import Path
import os

from dotenv import load_dotenv
from pymilvus import MilvusClient
from rich import print as rprint

from langchain.agents import create_agent
from langchain.embeddings import init_embeddings
from langchain_deepseek import ChatDeepSeek

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
load_dotenv()

MILVUS_URI = "http://localhost:19530"  # Milvus 服务的连接地址
DB_NAME = "rag_project1"    # 自定义数据库名称
COLLECTION_NAME = "docs"    # 向量集合名称（类似于传统数据库的表）
EMBED_DIM = 1024   # BGE-M3 模型输出的向量维度固定为 1024

DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL=os.getenv("DEEPSEEK_BASE_URL")


#初始化Milvus
client=MilvusClient(MILVUS_URI)
exist_databases=client.list_databases()
if DB_NAME not in exist_databases:
    client.create_database(db_name=DB_NAME)
client.use_database(db_name=DB_NAME)

#创建collection
if client.has_collection(collection_name=COLLECTION_NAME):
    client.drop_collection(collection_name=COLLECTION_NAME)
client.create_collection(
    collection_name=COLLECTION_NAME,
    dimension=EMBED_DIM,
    metric_type="COSINE"
)
#模型初始化
model=ChatDeepSeek(
    model="deepseek-v4-flash",
    api_key=DEEPSEEK_API_KEY,
    api_base=DEEPSEEK_BASE_URL,
    # 关键修改：关闭思考模式
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    },
)
questions = [
    # 普通知识：Agent 可以直接回答，不一定需要检索
    "2 加 2 等于多少？",
    "法国的首都是哪里？",
    "Python 是一种什么类型的编程语言？",

    # 文档相关：Agent 应该调用检索工具
    "在 Document 中，page_content 和 metadata 分别保存什么？",
    "chunk_size 和 chunk_overlap 分别有什么作用？",
    "向量 (1, 2) 和 (2, 1) 的余弦相似度是多少？",
    "similarity_search 中的 k=2 表示什么？",
    "使用 @tool 装饰器有什么作用？",

    # 项目专属问题：必须检索 08_qinghe_project.md
    "青禾笔记助手的项目代号是什么？",
    "青禾项目的 chunk_size、chunk_overlap 和检索数量分别是多少？",

    # 知识库中没有明确答案的问题
    "青禾项目什么时候正式上线？",
]

# 2. Create AzureOpenAIEmbeddings and ChatOpenAI instances
embedding_model=init_embeddings(
    model="openai:Pro/BAAI/bge-m3",
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url=os.getenv("SILICONFLOW_BASE_URL")
)
# 3. Create an array of Document objects:
#    - Use your own content as page_content
#    - Add metadata (title, source, etc.)
#读取文档并添加metadata
data_dir = Path(__file__).resolve().parent / "rag_assignment_materials" / "documents"
docs=[]
for file_path in sorted(data_dir.glob("*.md")):
    loader=TextLoader(str(file_path),encoding="utf-8")
    file_docs=loader.load()
    for doc in file_docs:
        doc.metadata['title']=file_path.stem
        doc.metadata['source']=file_path.name
        doc.metadata['date']='2026-9-13'
    docs.extend(file_docs)
#print(f"共加载 {len(docs)} 份文档")

#切分
splitter=RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
)
split_docs=splitter.split_documents(docs)
# print("切分前文档数：", len(docs))
# print("切分后片段数：", len(split_docs))
# for doc in split_docs:
#     print("来源信息：", doc.metadata)
#     print("片段正文：", doc.page_content)
#     print()
# 4. 生成向量并存入Milvus
text=[doc.page_content for doc in split_docs]
vectors=embedding_model.embed_documents(text)
data = [
    {
        "id": i,
        "vector": vectors[i],
        "text": doc.page_content,
        "source": doc.metadata["source"],
        "title": doc.metadata["title"],
        "date": doc.metadata["date"],
    }
    for i, doc in enumerate(split_docs)
]
insert_res=client.upsert(
    collection_name=COLLECTION_NAME,
    data=data
)
# 5. Create a retrieval tool using @tool decorator:
#    - Define function that searches vector store
#    - Provide clear name and description
#    - Format results with source attribution
@tool
def search_my_notes(query: str) -> str:
    """搜索个人 LangChain 学习资料，包括青禾项目说明和配置。"""
    print("正在检索：", query)

    query_vector = embedding_model.embed_query(query)

    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=5,
        output_fields=["text", "source"],
    )

    # 只传入了一个问题向量，所以取第一组搜索结果
    hits = results[0]

    if not hits:
        return "没有检索到资料。"

    return "\n\n".join(
        f"[{hit['entity']['source']}]\n{hit['entity']['text']}"
        for hit in hits
    )
# 6. Create agent with create_agent():
#    - Pass model and tools list
#    - Add system_prompt for context
#    - Agent will decide when to use retrieval tool

agent = create_agent(
    model=model,
    tools=[search_my_notes],
    system_prompt= "你是一个中文 LangChain 学习助手。"
        "当问题涉及我的学习资料、青禾项目或具体配置时，必须调用 search_my_notes 工具。"
        "普通常识问题可以直接回答。"
        "如果知识库没有足够依据，请明确说明，不要编造。"
        "使用知识库内容回答时，请注明来源文件名。"
)

# 7. Test with questions that demonstrate agent decision-making:
#    - General knowledge (agent answers directly)
#    - Document-specific (agent searches)
#    - Questions not in docs (agent may search but won't find)
for question in questions:
    response = agent.invoke({
        "messages": [HumanMessage(content=f"{question}")]
    })
    final_message=response["messages"][-1]
    print("回答：")
    rprint(final_message.content)
    for message in response["messages"]:
        if getattr(message, "tool_calls", None):
            print("本次调用了检索工具：", message.tool_calls)
