# Agentic RAG 作业：中文知识库素材

已准备 8 份 UTF-8 Markdown 文档，主题为 LangChain 与 RAG 入门，适用于微软作业中的“准备 5～10 份资料”步骤。

这些是为练习原创整理的示例资料，不是官方中文译文，不冒充用户本人写过的笔记或博客。第 8 份包含明确标注的虚构项目事实，用于检验 Agent 是否实际检索了知识库。技术接口参考链接附在相关文档中，整理日期为 2026-09-13。

作业来源：[微软第 8 章个人知识库问答作业](https://github.com/microsoft/langchain-for-beginners/blob/main/08-agentic-rag-systems/assignment.md)。

## 资料清单

1. documents/01_documents.md：Document、正文、元数据和文件来源。
2. documents/02_splitting.md：切分长度、重叠和中文切分。
3. documents/03_embeddings.md：嵌入模型和余弦相似度。
4. documents/04_vector_store.md：内存向量库、检索数量和无关结果。
5. documents/05_retrieval_tool.md：@tool、工具描述和 Agent 调用过程。
6. documents/06_rag_workflow.md：传统 RAG、Agentic RAG 和引用。
7. documents/07_memory.md：对话历史、短期记忆和重置。
8. documents/08_qinghe_project.md：虚构的青禾笔记助手项目约定。

## 如何使用

只将 documents 文件夹内的 8 个 .md 文件加载进知识库。README.md 和 questions.md 是操作与验证说明，不应作为检索资料导入。

Markdown 本身是文本，可以使用 TextLoader 按 UTF-8 读取，不必额外安装复杂的 Markdown 解析器。也可以用 Path.read_text(encoding='utf-8') 读取后自己创建 Document。

每个文件对应一个初始 Document。source 建议设置为实际文件名；title 可以取文件第一行标题。随后再切分，并保留元数据。不要把参考网站链接误当作本文的实际来源文件名。

资料中出现的代码名称和参数都是文档内容，不需要作为 Python 代码执行。本素材包没有修改模型配置，没有运行嵌入接口，也没有写入向量库。

## 检查效果

questions.md 包含测试问题、预期来源和核对要点。它不是自动测试脚本，也不保证任何模型一定检索到正确结果。先验证加载与检索，再验证回答与引用。

像“什么是 LangChain”这类问题，模型可能凭已有知识回答。要确认真的查过资料，优先问“青禾项目的代号和检索参数是什么”，并检查工具调用记录以及检索片段。
