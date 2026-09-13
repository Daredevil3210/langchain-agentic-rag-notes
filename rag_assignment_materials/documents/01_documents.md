# 文档对象与来源信息

## 正文和元数据

LangChain 的 Document 用来表示一份文档或一个文档片段。page_content 保存正文字符串，metadata 保存附加信息。比如，一份介绍工具调用的笔记，可以把正文放进 page_content，把标题、来源文件名和分类放进 metadata。

metadata 中的 source 可以写成 tools.md，title 可以写成“工具调用笔记”。这些字段是资料标签。手动填写 source 不会让程序自动读取这个文件，也不能证明正文真的来自该文件。

## 加载文件

TextLoader 用来读取文本文件。创建加载器时指定文件路径，调用 load() 才读取文件。读取结果是 Document 列表；一个普通文本文件通常对应一个 Document。TXT 和纯文本形式的 Markdown 可以按 UTF-8 编码读取。

## 为什么保留来源

检索系统找到片段后，需要说明答案依据哪份资料。加载时保留 source，切分后检查来源是否仍在，才能把回答与原文对应起来。如果代码访问 metadata['source']，而该字段不存在，就会发生 KeyError；也可以使用 get('source', '未知来源') 提供默认值。

资料性质：为本次学习作业原创整理的中文示例笔记，不是用户的真实学习记录或官方译文。
