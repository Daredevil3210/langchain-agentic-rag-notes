**English** | [简体中文](README.zh.md)

# LangChain Agentic RAG Notes

A personal knowledge-base exercise that lets a LangChain agent decide when to retrieve information from Chinese Markdown notes. Four Python entrypoints compare in-memory retrieval with Milvus, and batch questions with a conversational terminal interface.

The collection includes eight learning documents, source attribution in retrieved context, follow-up questions, and examples where the notes do not contain an answer. The “Qinghe Notes Assistant” described in the materials is a fictional practice project.

## How the examples work

```text
Markdown notes → TextLoader → metadata → recursive splitting
→ hosted embeddings → InMemoryVectorStore or Milvus
→ agent-selected retrieval tool → grounded answer
```

Documents receive title, source filename, and date metadata. DeepSeek supplies the agent model; SiliconFlow supplies embeddings through an OpenAI-compatible API. The agent is prompted to retrieve learning-note and project-specific questions, answer general knowledge directly, cite filenames, and acknowledge insufficient evidence. Those prompts do not guarantee correct retrieval or answers.

## Choose an entrypoint

- [knowledge_base_rag.py](knowledge_base_rag.py): builds an in-memory index, runs a fixed set of general, document-specific, project-specific, and unanswered questions, then prints answers and any retrieval tool calls.
- [conversational_rag.py](conversational_rag.py): an in-memory terminal chat with follow-up questions and session reset.
- [knowledge_base_rag_Milvus.py](knowledge_base_rag_Milvus.py): manually embeds and writes records to Milvus, then runs the batch questions.
- [conversational_rag_Milvus.py](conversational_rag_Milvus.py): terminal chat backed by a dedicated Milvus collection, with document/vector validation and cleanup of stale chunk IDs.

The [assignment materials](rag_assignment_materials/README.md), [documents](rag_assignment_materials/documents/), and [question set](rag_assignment_materials/questions.md) explain the learning tasks.

## Set up

The repository does not include a pinned dependency manifest or declare a minimum Python version. Create an environment with a Python version supported by the selected LangChain packages. The original setup uses PowerShell:

```powershell
git clone https://github.com/Daredevil3210/langchain-agentic-rag-notes.git
cd langchain-agentic-rag-notes
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install langchain langchain-community langchain-text-splitters langchain-openai langchain-deepseek python-dotenv rich
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Fill in your local configuration from [.env.example](.env.example):

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=your_deepseek_base_url
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_BASE_URL=your_siliconflow_base_url
```

Keep real credentials local. All four scripts use online embeddings and chat, so they require network access and valid provider configuration and may incur charges. Current code requests `deepseek-v4-flash` and `Pro/BAAI/bge-m3`; change those names in the scripts if your account needs different models.

## Run the in-memory examples

From the repository root:

```powershell
python knowledge_base_rag.py
python conversational_rag.py
```

The first command completes its question list; the second opens a chat prompt. Try these questions in sequence:

```text
青禾笔记助手的项目代号是什么？
这个项目的 chunk_size 和 chunk_overlap 分别是多少？
它什么时候正式上线？
reset
2 加 2 等于多少？
exit
```

The conversational scripts print the actual search query and return source filenames with retrieved material. `reset` clears message history while retaining the knowledge base; `exit` or `quit` ends the process; empty input is ignored. History retains user messages and final answers, not the complete tool-call trace, and is lost when the process exits.

## Run with Milvus

Install the client and start a reachable Milvus server before running either Milvus entrypoint. The Python client does not start a database service.

```powershell
python -m pip install pymilvus
python knowledge_base_rag_Milvus.py
# Or, for interactive follow-up questions:
python conversational_rag_Milvus.py
```

Review the script constants first:

```python
MILVUS_URI = "http://localhost:19530"
DB_NAME = "rag_project1"
# Batch script: "docs"; conversational script: "docs_conversational"
EMBED_DIM = 1024
```

The scripts do not configure authentication; add the appropriate client configuration if your server requires it. The embedding output dimension must match EMBED_DIM. Collections use COSINE similarity and records include id, vector, text, source, title, and date. Retrieval requests text and source for the agent.

**Batch version:** every run drops the existing `rag_project1.docs` collection and recreates it before embedding and writing the notes. Use a dedicated practice collection. If later steps fail, the deleted data is not restored. There is no existing-index reuse or incremental synchronization. This entrypoint was renamed from `knowledge_base_rag - Milvus.py` in v0.4.0.

**Conversational version:** uses a separate `docs_conversational` collection. It creates the collection if absent; otherwise it keeps it. Each startup still re-embeds all notes, upserts chunks by numeric ID, and deletes old records beyond the new ID range. This avoids leftover chunks after notes shrink or splitting changes, but is neither a transaction nor a concurrent importer. Let only this script manage the collection, run one instance at a time, and rerun the full import after a failure.

The conversational Milvus script checks the document directory, empty content, vector count, and dimensions. It searches with Strong consistency to read newly written records. Reset clears chat history only; the database retains knowledge records, while chat history remains process-local.

## Retrieval settings and debugging

- In-memory batch: chunk size 400, overlap 80, at most 7 results.
- In-memory conversation: chunk size 400, overlap 80, at most 8 results.
- Milvus batch: chunk size 400, overlap 80, at most 5 results.
- Milvus conversation: chunk size 1200, overlap 150, at most 8 results.

The result limits count chunks, not Markdown files. Parameters described in the fictional project documents are exercise data and may differ from these runtime settings.

All entrypoints reload, split, and embed their notes on startup. In-memory indexes disappear when the process exits; Milvus batch rebuilds its collection, and Milvus conversation updates its collection. None skips embedding unchanged documents.

If the assistant misses an answer that exists in the notes, inspect the search query and retrieved chunks first. Returned chunks may not contain an answer, and retrieval may miss relevant material. Restart after changing documents, splitting, or embedding models to refresh the index.

The Milvus batch search does not explicitly set consistency. If new data is not visible immediately, inspect visibility and consider `consistency_level="Strong"`. The conversational version already uses it; consistency does not ensure relevance.

## CI mode and validation limits

Only the conversational entrypoints recognize the exact lowercase environment value `CI=true`. They still require input and real embedding/chat services, then exit after one successful answer. This is not an offline test mode:

```powershell
$env:CI = "true"
"2 + 2 = ?" | python conversational_rag.py
Remove-Item Env:CI
```

Use `conversational_rag_Milvus.py` to try the same flow with Milvus. The batch scripts do not use this setting. No automated test suite or pinned installation is included, and no scripts or online services were executed for this documentation refresh.

## Version history

- [v0.4.0](https://github.com/Daredevil3210/langchain-agentic-rag-notes/releases/tag/v0.4.0): conversational Milvus entrypoint, dedicated collection, stale-chunk cleanup, empty-content/vector validation, and batch script rename.
- [v0.3.0](https://github.com/Daredevil3210/langchain-agentic-rag-notes/releases/tag/v0.3.0): Milvus batch exercise, vectors and metadata, source-aware retrieval, database setup, rebuild notes, and conversational empty-result feedback.
- [v0.2.0](https://github.com/Daredevil3210/langchain-agentic-rag-notes/releases/tag/v0.2.0): conversational entrypoint, reset/exit commands, CI single-answer mode, corrected reset handling, and consistent source filenames.
- [v0.1.0](https://github.com/Daredevil3210/langchain-agentic-rag-notes/releases/tag/v0.1.0): initial knowledge-base exercise and eight Chinese Markdown documents.

## License

[MIT License](LICENSE). The Chinese assignment materials were prepared for the LangChain Agentic RAG learning exercise.
