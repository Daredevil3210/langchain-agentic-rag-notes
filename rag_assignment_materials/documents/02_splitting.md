# 文档切分与重叠

## 为什么切分

一本长笔记可能包含多个主题。把整本笔记作为一个检索单位，会使问题对应的细节难以单独返回。切分是把正文拆成较小片段，便于检索后只向模型提供相关内容。

## 两个参数

RecursiveCharacterTextSplitter 根据分隔符递归拆分文本。使用默认长度函数 len 时，chunk_size 按字符计数，不是按 token 计数。chunk_overlap 是相邻片段的目标重叠长度，实际重叠受切分边界影响。

例如，chunk_size=400、chunk_overlap=80 是一组练习参数，不是所有资料的最佳配置。重叠可以保留跨边界的上下文，但也会增加重复内容。中文资料可以增加句号、逗号等分隔符，并保留空字符串作为最终拆分方式。

## 输入与输出

split_documents([doc]) 接收 Document 列表，返回切分后的 Document 列表。每个片段保留原文档的元数据。切分后应检查正文是否完整、来源是否保留，以及单个片段是否混入太多主题；不能仅凭片段数量判断效果。

资料性质：为本次作业整理的中文示例笔记。
参考：[LangChain 递归切分文档](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)。
