# 内存向量库与语义检索

## 建立向量库

InMemoryVectorStore 是 LangChain 提供的内存向量存储。from_documents(docs, embeddings) 会使用传入的嵌入模型计算文档向量，并保存正文、元数据和向量。它不要求部署独立数据库，适合小规模练习。

内存中的内容不会在 Python 进程结束后自动保存。要让应用重启后继续使用已有数据，需要显式保存并恢复，或者使用支持持久化的存储方案。

## 查询过程

similarity_search(question, k=2) 会计算问题的向量，与库中的文档向量比较，并返回最相关的最多两份 Document。这里的 k 表示结果数量，不是相似度阈值，也不是模型回答的句子数。这个内存向量库使用余弦相似度进行比较。

## 返回结果的限制

similarity_search 返回文档对象，既不是最终答案，也不是只有数字的向量。只要库中有数据，前 k 个结果中也可能全是无关内容。因此，检索结果非空不能证明知识库中存在答案，还需要检查片段是否支持问题。

资料性质：为本次作业整理的中文示例笔记。
参考：[LangChain 内存向量库文档](https://docs.langchain.com/oss/python/integrations/vectorstores/in_memory)。
