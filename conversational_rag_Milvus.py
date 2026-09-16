from pathlib import Path
import os
from pymilvus import MilvusClient
from dotenv import load_dotenv
from langchain_core.documents import Document
from rich import print as rprint

from langchain.agents import create_agent
from langchain.embeddings import init_embeddings
from langchain_deepseek import ChatDeepSeek

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
MILVUS_URI = "http://localhost:19530"  # Milvus 服务的连接地址
DB_NAME = "rag_project1"    # 自定义数据库名称
COLLECTION_NAME = "docs_conversational"  # 多轮对话专用集合，避免与批量版混用
EMBED_DIM = 1024   # BGE-M3 模型输出的向量维度固定为 1024
# knowledge_base = [
#     Document(
#         page_content="Python is a high-level, interpreted programming language known for its readability and simplicity. It was created by Guido van Rossum and first released in 1991.",
#         metadata={"title": "Python Overview", "section": "Introduction"},
#     ),
#     Document(
#         page_content="Python's main benefits include easy-to-read syntax, extensive standard library, cross-platform compatibility, and strong community support. It's used for web development, data science, AI, and automation.",
#         metadata={"title": "Python Benefits", "section": "Advantages"},
#     ),
#     Document(
#         page_content="Python uses duck typing and dynamic typing. Variables don't need type declarations, though type hints are supported since Python 3.5+ for better code documentation and IDE support.",
#         metadata={"title": "Python Type System", "section": "Type System"},
#     ),
#     Document(
#         page_content="Python decorators are a powerful feature that allows you to modify or enhance functions and classes. Common decorators include @property, @staticmethod, @classmethod, and custom decorators using functools.wraps.",
#         metadata={"title": "Python Decorators", "section": "Advanced Features"},
#     ),
#     Document(
#         page_content="Python's list comprehensions provide a concise way to create lists based on existing sequences. They're more readable and often faster than traditional for loops for simple transformations.",
#         metadata={"title": "List Comprehensions", "section": "Core Features"},
#     ),
# ]

def main():
    print("💬 Conversational Agentic RAG System\n")
    print("=" * 80 + "\n")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
    # 2.模型初始化
    model = ChatDeepSeek(
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

    embedding_model = init_embeddings(
        model="openai:Pro/BAAI/bge-m3",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url=os.getenv("SILICONFLOW_BASE_URL")
    )
    # 初始化Milvus
    client = MilvusClient(MILVUS_URI)
    exist_databases = client.list_databases()
    if DB_NAME not in exist_databases:
        client.create_database(DB_NAME)
    client.use_database(DB_NAME)

    # 创建collection（不存在才创建）
    if not client.has_collection(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            dimension=EMBED_DIM,
            metric_type="COSINE"
        )
    data_dir = Path(__file__).resolve().parent / "rag_assignment_materials" / "documents"
    docs = []
    if not data_dir.exists():
        raise FileNotFoundError(
            f"知识库目录不存在:{data_dir}"
        )
    for file_path in sorted(data_dir.glob("*.md")):
        loader = TextLoader(str(file_path), encoding="utf-8")
        file_docs = loader.load()
        for doc in file_docs:
            doc.metadata['title'] = file_path.stem
            doc.metadata['source'] = file_path.name
            doc.metadata['date'] = '2026-9-13'
        docs.extend(file_docs)
    if not docs:
        raise ValueError("没有读取到任何Markdown文档")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    knowledge_base = splitter.split_documents(docs)
    if not knowledge_base:
        raise ValueError("Markdown文档没有可用的正文片段")
    print(f"Creating vector store with {len(knowledge_base)} documents...\n")
    text=[doc.page_content for doc in knowledge_base]
    vectors=embedding_model.embed_documents(text)
    if len(vectors) != len(knowledge_base) or any(len(v) != EMBED_DIM for v in vectors):
        raise ValueError("嵌入向量数量或维度与文档及集合配置不匹配")
    data=[
        {
            "id": i,
            "vector": vectors[i],
            "text": doc.page_content,
            "source": doc.metadata["source"],
            "title": doc.metadata["title"],
            "date": doc.metadata["date"],
        }
        for i, doc in enumerate(knowledge_base)
    ]
    insert_res=client.upsert(
        collection_name=COLLECTION_NAME,
        data=data
    )
    # 新片段使用 0 到 len(data)-1 的编号；清理上次导入多出的尾部记录。
    # 此集合只由本脚本管理，导入时不要并发运行多个实例。
    client.load_collection(collection_name=COLLECTION_NAME)
    client.delete(
        collection_name=COLLECTION_NAME,
        filter=f"id >= {len(data)}",
    )
    #vector_store = InMemoryVectorStore.from_documents(knowledge_base,embedding_model)

# 1. Create retrieval tool as in Challenge 1
    @tool
    def search_python_knowledge_base(query: str) -> str:
        """
        用于查询内部知识库。
        必须用于：
        1. LangChain学习资料
        2. 青禾项目配置
        3. chunk参数
        4. Milvus配置
        5. 项目代码说明
        不要用于普通数学、地理、编程基础知识。
        """
        print(f'   🔍 Agent searching for: "{query}"')
        #results=vector_store.similarity_search(query,k=8)
        query_vector=embedding_model.embed_query(query)
        results=client.search(
            collection_name=COLLECTION_NAME,
            data=[query_vector],
            limit=8,
            output_fields=["text","source"],
            consistency_level="Strong",
        )
        hits = results[0]

        if not hits:
            return "没有检索到资料。"

        return "\n\n".join(
            f"[{hit['entity']['source']}]\n{hit['entity']['text']}"
            for hit in hits
        )
# 2. Create agent with create_agent()
    agent=create_agent(
        model=model,
        tools=[search_python_knowledge_base],
        system_prompt=("你是一个中文 LangChain 学习助手。"
        "当问题涉及我的学习资料、青禾项目或具体配置时，必须调用 search_python_knowledge_base 工具。"
        "普通常识问题可以直接回答。"
        "如果知识库没有足够依据，请明确说明，不要编造。"
        "使用知识库内容回答时，请注明来源文件名。"
        "结合对话历史理解用户的追问，"
        "检索时把“它”“这个项目”等指代转换成明确的搜索词。"),
    )
# 3. Initialize empty message history list
    conversation_history: list[HumanMessage | AIMessage] = []
    print("💡 Instructions:")
    print("   - Ask questions about Langchain")
    print("   - Ask follow-up questions to test conversation memory")
    print("   - Type 'reset' to start a new conversation")
    print("   - Type 'exit' or 'quit' to end\n")
    print("=" * 80 + "\n")
    is_ci = os.getenv("CI") == "true"
    question_count=0
    while(True):
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print("\n👋 Goodbye! Thanks for chatting!\n")
            break
        if user_input.lower() in ("exit", "quit"):
            print("\n👋 Goodbye! Thanks for chatting!\n")
            break
        if user_input.lower() == "reset":
            conversation_history.clear()
            print("\n🔄 Conversation reset. Starting fresh!\n")
            continue
        if not user_input:
            continue
# 4. For each user question:
#    - Add new HumanMessage with user input to history
#    - Invoke agent with full message history
#    - Display agent's response
#    - Add agent's response to history
#    - Continue conversation loop

        conversation_history.append(HumanMessage(content=user_input))
        try:
            response = agent.invoke({
                "messages": list(conversation_history),
            })
            agent_message = response["messages"][-1]
            conversation_history.append(AIMessage(content=agent_message.content))
            print(f"\nAgent: {agent_message.content}\n")
            print("=" * 80 + "\n")
            #In CI mode, exit after answering one question
            question_count += 1
            if is_ci and question_count >= 1:
                print("✅ CI Mode: Answered one question successfully. Exiting.\n")
                break
        except Exception as e:(
            print(f"Error: {e}"))
if __name__ == "__main__":
    main()
# 5. Handle special commands:
#    - "exit" or "quit" to end conversation
#    - "reset" to clear history and start fresh

# 6. The agent will autonomously:
#    - Understand context from conversation history
#    - Decide when to search documents
#    - Answer follow-up questions intelligently
