# Week-by-Week Schedule (Compact)

This condensed schedule maps the one-month program into weekly goals and concrete tasks.

## Week 1 — Foundations & Setup

- Goals: Learn RAG basics, install Foundry Local, verify the environment.
- Tasks: create venv, run `python check_setup.py`, run the hello-model script: `python examples/hello_model.py`.
- Deliverable: Setup checker passes; first local model inference works.

## Week 2 — Embeddings & Vector Store

- Goals: Generate embeddings, understand cosine similarity, build a small SQLite vector store.
- Tasks: run `python examples/embedding_demo.py` and `python examples/sql_sandbox.py`; then `python ingest.py` to build `rag.db`; test `retrieval.py` for sample queries.
- Deliverable: Populated `rag.db` and verified top-k retrieval.

## Week 3 — Ingestion Pipeline & Retrieval

- Goals: Chunk documents, tune chunk size/overlap, make retrieval robust for your doc set.
- Tasks: add or edit `data/` documents, tweak `ingest.py` (`MAX_CHARS`, `OVERLAP`), re-run ingestion, save retrieval examples.
- Deliverable: Team-specific knowledge base with reliable get_top_chunks() behavior.

## Week 4 — LLM Integration & UI

- Goals: Wire retrieval into the local LLM and provide a user interface.
- Tasks: implement `answer_query()` using `foundry_client.py`; choose CLI or `ui_streamlit.py`; tune `SYSTEM_PROMPT`.
- Deliverable: End-to-end assistant that answers grounded queries and shows sources.

## Week 5 — Testing & Evaluation

- Goals: Build an eval set and measure correctness and failure modes.
- Tasks: populate `eval/questions.yaml` (answerable, unanswerable, and edge cases), run `python eval/run_eval.py`, analyze fails and iterate.
- Deliverable: Test results recorded in `eval/results.md` and a short improvement plan.

## Week 6 — Documentation & Demo

- Goals: Finalize README, rehearse demo, and polish code/comments.
- Tasks: update `README.md`, remove debug logs, prepare the demo using [presentation_outline.md](presentation_outline.md), rehearse on the presentation machine.
- Deliverable: Rehearsed demo and final README with run instructions.

## Quick commands (copy-paste)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python check_setup.py
python examples/hello_model.py
python ingest.py
python main.py
streamlit run ui_streamlit.py
python eval/run_eval.py --verbose
```

## Notes

- For small datasets, brute-force similarity in Python is fine; for larger sets use a vector DB.
- Emphasize prompt instructions: "Answer only using the provided context; say 'I don't know' if not found."
