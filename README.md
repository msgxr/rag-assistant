# Local RAG Assistant — Python + Streamlit + SQLite + Foundry Local

Fully offline document Q&A assistant. Retrieves relevant chunks from local documents,
injects them into the prompt, and asks an on-device Foundry Local model to generate
a source-grounded answer. No cloud, no API keys, no internet required after the
initial model download.

> **Reference project:** [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)
> **Teaching plan:** [`docs/one_month_plan.md`](docs/one_month_plan.md)

---

## Architecture

```
[User / UI]       ui_streamlit.py  ·  main.py (CLI)
      ↓
[Application]     generation.answer_query()
      ↓               ↳ prompts.build_user_message()
[RAG Retrieval]   retrieval.get_top_chunks()  ←  ingest.py (one-time)
      ↓                                              ↳ chunk_text()
[Data Layer]      rag.db (SQLite)  ←  db.py
      ↓
[AI Layer]        foundry_client.chat() / get_embedding()
                      ↳ Foundry Local Runtime — 100% on-device, offline
```

**Ingest flow:** `data/*.md` → `ingest.py` → `chunk_text()` → embedding → `rag.db`

**Query flow:** question → `answer_query()` → `get_top_chunks()` → `rag.db` → prompt → `fc.chat()` → answer

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.10+ | 3.11 recommended |
| Windows or Apple Silicon Mac | Intel Mac not supported by Foundry Local |
| ~4 GB free disk | For model download (first run only) |
| Internet (first run only) | Model cached after first download |

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python check_setup.py

# 4. (Optional) List all available model aliases
python check_setup.py --models
```

If `check_setup.py` reports that a model alias is missing, edit `foundry_client.py`:

```python
CHAT_MODEL_ALIAS      = "qwen2.5-0.5b"       # or: phi-3.5-mini, phi-4-mini
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
```

---

## Quick Start

```bash
# Step 1 — Build the knowledge base (run whenever data/ changes)
python ingest.py

# Step 2a — CLI interface
python main.py

# Step 2b — Streamlit web UI
streamlit run ui_streamlit.py
```

Add your own `.txt` or `.md` files to `data/`, then rerun `python ingest.py`.
Ingestion clears and rebuilds the `documents` table each time.

---

## Evaluation

```bash
python eval/run_eval.py              # run all 23 test questions
python eval/run_eval.py --verbose    # show full answers
python eval/run_eval.py --fail-only  # show only failures
```

The evaluation set (`eval/questions.yaml`) checks:
- **Answerable questions** — the assistant should answer from the documents and cite sources
- **Unanswerable questions** — the assistant should say it doesn't have that information

---

## Project Files

| File | Purpose |
|------|---------|
| `foundry_client.py` | Single wrapper around the Foundry Local SDK |
| `db.py` | SQLite schema (`documents` table) and helpers |
| `ingest.py` | Reads, chunks, embeds, and stores `data/` documents |
| `retrieval.py` | Embeds a query, returns top-K matching chunks |
| `prompts.py` | System prompt + context message builder |
| `generation.py` | End-to-end `answer_query()` pipeline |
| `main.py` | CLI Q&A loop |
| `ui_streamlit.py` | Streamlit web UI with sidebar and debug panel |
| `check_setup.py` | Environment, catalog, alias, data, and DB checker |
| `eval/questions.yaml` | 23 test questions (answerable + unanswerable) |
| `eval/run_eval.py` | Evaluation runner with timing and summary |
| `docs/one_month_plan.md` | Full 6-week teaching schedule |
| `data/*.md` | Knowledge base documents (6 files) |

---

## Knowledge Base Documents

| File | Topic |
|------|-------|
| `rag_nedir.md` | RAG overview, hallucination, three-step pipeline |
| `foundry_local.md` | Installation, model management, hardware support |
| `embeddings.md` | Embeddings, cosine similarity, top-K retrieval |
| `sqlite.md` | SQLite overview, schema, SQL operations, limitations |
| `prompt_engineering.md` | System/user prompts, RAG prompt design, pitfalls |
| `rag_pipeline.md` | Ingestion and query phases explained step by step |

---

## Interface Contract

```python
# foundry_client.py
foundry_client.get_embedding(text: str) -> list[float]
foundry_client.chat(messages: list[dict]) -> str
foundry_client.shutdown() -> None

# retrieval.py
retrieval.get_top_chunks(query: str, k: int = 3) -> list[dict]
# Returns: [{"text": str, "source": str, "score": float}, ...]

# generation.py
generation.answer_query(question: str) -> dict
# Returns: {"answer": str, "sources": list[str], "used_chunks": list[dict]}
```

---

## Key Configuration

All tunable constants are at the top of their respective files:

| Constant | File | Default | Effect |
|----------|------|---------|--------|
| `CHAT_MODEL_ALIAS` | `foundry_client.py` | `qwen2.5-0.5b` | LLM for answer generation |
| `EMBEDDING_MODEL_ALIAS` | `foundry_client.py` | `qwen3-embedding-0.6b` | Embedding model |
| `TEMPERATURE` | `foundry_client.py` | `0.2` | Answer randomness |
| `MAX_TOKENS` | `foundry_client.py` | `512` | Max answer length |
| `TOP_K` | `generation.py` | `3` | Chunks retrieved per query |
| `MIN_RELEVANCE_SCORE` | `generation.py` | `0.45` | Minimum cosine similarity |
| `MAX_CHARS` | `ingest.py` | `800` | Target chunk size (characters) |
| `OVERLAP` | `ingest.py` | `100` | Chunk overlap (characters) |

---

## Definition of Done

- [ ] `python check_setup.py` passes with no errors
- [ ] `python ingest.py` creates chunks in `rag.db`
- [ ] CLI or Streamlit accepts questions and returns grounded answers with sources
- [ ] Unanswerable questions get a fallback response (no hallucination)
- [ ] `python eval/run_eval.py` runs and results are recorded
- [ ] `README.md` updated with any team-specific notes
- [ ] Final demo rehearsed on the target machine

---

## License

MIT — This project is a teaching sample for learning and experimentation.
