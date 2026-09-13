# 检索工具与 Agent

## 把搜索功能交给模型

使用 @tool 可以把检索函数包装成 Agent 能调用的工具。例如，search_notes 接收 query 字符串，在函数内部调用向量库搜索，然后返回带来源标记的正文。函数的文档字符串默认作为工具描述，参数类型提示用于定义输入结构。

工具描述应说明资料范围和适用问题。“搜索学习笔记中关于文档、嵌入和记忆的说明”比“搜索一些东西”更容易让模型理解用途。工具名本身不会让它获得联网搜索能力；它能查什么，取决于函数内部实现。

## 调用过程

create_agent(model, tools=[search_notes], system_prompt=...) 创建带检索工具的 Agent。列表中传入工具对象，不写 search_notes()。创建 Agent 时不会立即检索；调用 agent.invoke 后，模型才会根据问题和指令选择工具及参数。

运行机制执行工具，将资料交回模型，模型再生成回答。工具的返回文本是参考材料，不一定就是面向用户的最终答案。验证检索功能时，应查看实际工具调用记录，不能只看回答里有没有出现文档名称。

资料性质：为本次作业整理的中文示例笔记。
参考：[LangChain 工具文档](https://docs.langchain.com/oss/python/langchain/tools)、[Agent 文档](https://docs.langchain.com/oss/python/langchain/agents)。
