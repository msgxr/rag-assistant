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

# 5. "Hello Model" smoke test — loads the chat model and prints one completion
python examples/hello_model.py
```

If `check_setup.py` reports that a model alias is missing, edit `foundry_client.py`:

```python
CHAT_MODEL_ALIAS      = "qwen2.5-1.5b"        # or: qwen2.5-0.5b, phi-3.5-mini
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
python eval/run_eval.py              # run all 26 test questions
python eval/run_eval.py --verbose    # show full answers
python eval/run_eval.py --fail-only  # show only failures
```

The evaluation set (`eval/questions.yaml`) checks:
- **Answerable questions** — the assistant should answer from the documents and cite sources
- **Unanswerable questions** — the assistant should say it doesn't have that information
- **Edge cases** — empty input, single-word, very general, and very long questions must be handled gracefully (no crash, no error answer)

Every run also writes a persistent report to `eval/results.md` (per-question PASS/FAIL, timing, sources) so test results are documented for the final report.

**Known weak spots / improvement list** (from the recorded runs):

- The 1.5B chat model sometimes paraphrases instead of using the literal expected
  token (e.g. describes hardware acceleration without the word "GPU", or explains
  the threshold without quoting "0.45"), so keyword checks can fail on acceptable
  answers. Next step: accept multiple keywords per question or grade answers with
  a second model pass.
- Rarely the model declines an answerable question (run-to-run variance even at
  `TEMPERATURE=0.2`). The strong-retrieval passage fallback (`STRONG_SCORE`)
  covers most of these; a retry-on-refusal would cover the rest.
- Merged (larger) chunks improved answer grounding but increased per-question
  latency on a CPU-only laptop. Next step: trim context to top-2 chunks for short
  questions, or run on NPU/GPU hardware.

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
| `eval/questions.yaml` | 26 test questions (18 answerable, 4 unanswerable, 4 edge) |
| `eval/run_eval.py` | Evaluation runner with timing, summary, and `eval/results.md` report |
| `examples/hello_model.py` | Week 1 exercise — "Hello Model" runtime smoke test |
| `examples/embedding_demo.py` | Week 2 exercise — embeddings + cosine similarity in memory |
| `examples/sql_sandbox.py` | Week 2 exercise — SQLite basics with the project schema |
| `docs/one_month_plan.md` | Full 6-week teaching schedule |
| `docs/week_by_week_schedule.md` | Compact week-by-week goals and tasks |
| `docs/presentation_outline.md` | Demo-day presentation outline |
| `data/*.md` | Knowledge base documents (7 files) |

---

## Knowledge Base Documents

| File | Topic |
|------|-------|
| `architecture.md` | This project's five-layer local architecture (client, application, retrieval, data, AI) |
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
| `CHAT_MODEL_ALIAS` | `foundry_client.py` | `qwen2.5-1.5b` | LLM for answer generation |
| `EMBEDDING_MODEL_ALIAS` | `foundry_client.py` | `qwen3-embedding-0.6b` | Embedding model |
| `TEMPERATURE` | `foundry_client.py` | `0.2` | Answer randomness |
| `MAX_TOKENS` | `foundry_client.py` | `256` | Max answer length |
| `TOP_K` | `generation.py` | `3` | Chunks retrieved per query |
| `MIN_RELEVANCE_SCORE` | `generation.py` | `0.45` | Minimum cosine similarity |
| `STRONG_SCORE` | `generation.py` | `0.60` | Above this, show best passage if the model gives up |
| `MAX_CHARS` | `ingest.py` | `800` | Target chunk size (characters) |
| `OVERLAP` | `ingest.py` | `100` | Chunk overlap (characters) |
| `MIN_CHARS` | `ingest.py` | `150` | Shorter pieces (headings, code lines) merge with neighbors |

---

## Design Decisions & Limitations

### Design decisions

- **Brute-force cosine similarity instead of a vector database.** For a 5–10 document
  knowledge base, comparing the query vector against every stored vector in Python is
  fast and needs zero extra dependencies. A dedicated vector DB (or a SQLite vector
  extension) only becomes necessary at much larger scale.
- **SQLite via the built-in `sqlite3` module.** Single file, serverless,
  cross-platform — ideal for a single-user local app. Embeddings are stored as
  JSON-serialized text for simplicity and easy debugging.
- **Paragraph-based chunking** (`MAX_CHARS=800`, `OVERLAP=100`). Paragraphs keep
  semantic units intact; the overlap prevents context loss when a long paragraph is
  split mid-thought.
- **`TOP_K=3` chunks per query with a `MIN_RELEVANCE_SCORE=0.45` gate.** Off-topic
  questions fall below the threshold and get an honest "I don't have that
  information" answer instead of a fabricated one. If the model itself declines,
  that refusal is respected and normalized to the same fallback sentence — unless
  retrieval is very strong (`STRONG_SCORE=0.60`), in which case the most relevant
  passage is shown with its source instead of losing a findable answer.
- **Small models for speed** (`qwen2.5-1.5b` chat, `qwen3-embedding-0.6b`
  embeddings) with `TEMPERATURE=0.2` for factual, consistent answers. The plan
  prioritizes fast feedback over answer depth; on this project's test machine
  `qwen2.5-0.5b` was faster but too weak in Turkish, and `phi-3.5-mini` was far
  too slow on CPU (~2 min/answer), so the 1.5B model is the measured sweet spot.
  Both models are loaded once at startup (warm-up), so the first question
  answers as fast as the rest.

### Limitations

- Answer quality is bounded by a ~3–4B parameter on-device model; long or subtle
  reasoning questions may get shallow answers.
- No incremental ingestion: `ingest.py` clears and rebuilds the `documents` table on
  every run (acceptable at this scale, wasteful for large corpora).
- Brute-force retrieval scales linearly with chunk count; beyond a few thousand
  chunks a vector index would be needed.
- SQLite here is single-user; concurrent writers are not supported.
- Foundry Local does not support Intel Macs (Windows / Apple Silicon only).
- Bilingual (Turkish/English) prompting can occasionally produce mixed-language
  answers with very small models.

---

## Definition of Done

- [x] `python check_setup.py` passes with no errors
- [x] `python ingest.py` creates chunks in `rag.db`
- [x] CLI or Streamlit accepts questions and returns grounded answers with sources
- [x] Unanswerable questions get a fallback response (no hallucination)
- [x] `python eval/run_eval.py` runs and results are recorded in `eval/results.md`
- [x] `README.md` updated with any team-specific notes
- [ ] Final demo rehearsed on the target machine

---

## License

MIT — This project is a teaching sample for learning and experimentation.
