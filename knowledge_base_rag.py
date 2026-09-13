# 1. Import required modules
from pathlib import Path
import os

from dotenv import load_dotenv
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

DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL=os.getenv("DEEPSEEK_BASE_URL")
#2.模型初始化
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
# 4. Create an InMemoryVectorStore from your documents
vector_store=InMemoryVectorStore.from_documents(split_docs,embedding_model,)

# 5. Create a retrieval tool using @tool decorator:
#    - Define function that searches vector store
#    - Provide clear name and description
#    - Format results with source attribution
@tool
def search_my_notes(query: str) -> str:
    """当需要获取相关信息时，可以搜索我的知识库"""
    print("正在检索:")
    results = vector_store.similarity_search(query, k=7)
    # if not results:
    #     return "知识库中没有找到相关资料。"
    return "\n\n".join(
         f"[{doc.metadata.get('source', '未知来源')}]: {doc.page_content}"
        for doc in results
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



# query = "青禾笔记助手的项目代号是什么？"
#
# results = vector_store.similarity_search(query, k=5)
#
# for i, doc in enumerate(results, 1):
#     print(f"\n第 {i} 条")
#     print("来源：", doc.metadata.get("source"))
#     print("内容：", doc.page_content[:300])
#
# for doc in split_docs:
#     if "QH-NOTES-08" in doc.page_content:
#         print("找到了项目代号")
#         print(doc.metadata)
#         print(doc.page_content)
