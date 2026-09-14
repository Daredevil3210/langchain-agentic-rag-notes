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
- 支持终端多轮对话，将用户问题和最终回答保存在当前会话中。
- 支持 `reset` 清空对话、`exit` / `quit` 退出，以及 CI 模式下回答一个问题后退出。

## 项目结构

```text
.
├── knowledge_base_rag.py
├── conversational_rag.py
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

在项目根目录创建并激活 Python 虚拟环境，然后安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install langchain langchain-community langchain-text-splitters langchain-openai langchain-deepseek python-dotenv rich
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

首次配置时复制环境变量模板；已有 `.env` 时跳过复制，保留自己的配置。填写 API 配置后运行脚本。嵌入和问答会调用在线服务，需要网络及有效的 API 配置。

### 批量问题测试

```powershell
python knowledge_base_rag.py
```

程序会依次测试问题，并打印最终回答以及是否调用了检索工具。

### 多轮对话

```powershell
python conversational_rag.py
```

输入问题后按回车，例如依次输入：

```text
青禾笔记助手的项目代号是什么？
这个项目的 chunk_size 和 chunk_overlap 分别是多少？
它什么时候正式上线？
reset
2 加 2 等于多少？
exit
```

- 普通知识可以直接回答；学习资料、青禾项目及具体配置问题按提示要求检索。
- 检索时会打印实际搜索词，返回资料包含来源文件名。
- `reset` 清空当前对话历史，保留已经创建的知识库。
- `exit` 或 `quit` 退出程序，空输入会被忽略。
- 对话历史只保存用户消息和最终回答，不保存完整工具调用过程；关闭程序后不会保留历史。

### CI 模式

只有环境变量 `CI` 的值为小写字符串 `true` 时才启用：成功回答一个问题后自动退出。它仍需输入问题，也仍然调用真实的嵌入和问答服务，并不是离线测试模式。

```powershell
$env:CI = "true"
"2 + 2 = ?" | python conversational_rag.py
Remove-Item Env:CI
```

## 当前实现与检索调试

两个脚本都使用 `chunk_size=400`、`chunk_overlap=80`；批量测试脚本当前使用 `k=7`，多轮对话脚本使用 `k=8`。`k` 表示返回的片段数量，不是 Markdown 文件数量。示例资料中记录的项目参数是练习设定，可能与脚本当前调试参数不同。

当前代码使用 DeepSeek 的 `deepseek-v4-flash` 和 SiliconFlow 的 `Pro/BAAI/bge-m3`，具体可用性取决于账号和接口配置；需要更换时修改脚本中的模型名称。向量库保存在内存中，每次启动都会重新加载、切分并生成向量。

如果资料中有答案但回答“不知道”，先查看实际搜索词及返回片段，确认答案是否进入检索结果。检索出片段不代表一定存在答案，也不能保证每次都召回正确片段。修改文档、切分参数或嵌入模型后，重新启动程序以重建向量库。

## 版本记录

- [v0.2.0](https://github.com/Daredevil3210/langchain-agentic-rag-notes/releases/tag/v0.2.0)：新增多轮对话入口、会话重置与退出、CI 单轮运行说明，修正重置命令判断并统一使用来源文件名。
- [v0.1.0](https://github.com/Daredevil3210/langchain-agentic-rag-notes/releases/tag/v0.1.0)：首个个人知识库 Agentic RAG 示例和 8 份中文 Markdown 资料。

## 资料说明

`rag_assignment_materials` 中的资料是为 LangChain Agentic RAG 学习作业整理的中文示例资料。第 8 份资料中的“青禾笔记助手”是虚构的练习项目。

## 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
