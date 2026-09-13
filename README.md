# LangChain Agentic RAG 学习项目

这是一个基于 LangChain 的个人知识库问答练习项目，使用中文 Markdown 学习资料构建 Agentic RAG。

项目流程：

```text
Markdown 文档
  → TextLoader 加载
  → RecursiveCharacterTextSplitter 切分
  → 嵌入模型向量化
  → InMemoryVectorStore 建库
  → Agent 调用检索工具
  → 根据资料回答问题
```

## 功能

- 加载 `rag_assignment_materials/documents` 下的 Markdown 文件。
- 为文档添加标题、来源和日期元数据。
- 使用递归字符切分器处理文档。
- 使用 SiliconFlow 的 OpenAI 兼容嵌入接口生成向量。
- 使用 DeepSeek 模型创建 LangChain Agent。
- Agent 根据问题决定是否调用知识库检索工具。
- 测试普通知识、资料相关和知识库未覆盖的问题。

## 项目结构

```text
.
├── knowledge_base_rag.py
└── rag_assignment_materials/
    ├── README.md
    ├── questions.md
    └── documents/
        ├── 01_documents.md
        ├── 02_splitting.md
        ├── 03_embeddings.md
        ├── 04_vector_store.md
        ├── 05_retrieval_tool.md
        ├── 06_rag_workflow.md
        ├── 07_memory.md
        └── 08_qinghe_project.md
```

## 配置环境变量

复制 `.env.example` 为 `.env`，然后填写自己的 API 配置。`.env` 只保存在本地，不要提交到 Git。

至少需要配置：

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=your_deepseek_base_url
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_BASE_URL=your_siliconflow_base_url
```

## 运行

安装项目使用的 LangChain、模型适配器、文档加载器、文本切分器、dotenv 和 rich 依赖后，在项目根目录运行：

```powershell
python knowledge_base_rag.py
```

程序会依次测试问题，并打印最终回答以及是否调用了检索工具。

## 资料说明

`rag_assignment_materials` 中的资料是为 LangChain Agentic RAG 学习作业整理的中文示例资料。第 8 份资料中的“青禾笔记助手”是虚构的练习项目。

## 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
