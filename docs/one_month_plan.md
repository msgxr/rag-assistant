# One-Month Project Plan: Local RAG AI Assistant with Microsoft Foundry Local

**Source:** [Microsoft Tech Community — Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)

**Goal:** Guide beginner computer science students through building a fully offline,
document-grounded Q&A assistant using Foundry Local (on-device LLM inference) and
the RAG (Retrieval-Augmented Generation) pattern. No cloud, no API keys, no internet
required after initial model download.

---

## Project Architecture (Quick Reference)

```
[User / UI]          ui_streamlit.py  or  main.py (CLI)
     ↓
[Application]        generation.answer_query()
     ↓                   ↳ prompts.build_user_message()
[RAG Retrieval]      retrieval.get_top_chunks()  ←  ingest.py (one-time setup)
     ↓                                                  ↳ ingest.chunk_text()
[Data Layer]         rag.db (SQLite)  ←  db.py schema
     ↓
[AI Layer]           foundry_client.chat() / get_embedding()
                         ↳ Foundry Local Runtime (on-device, offline)
```

**Ingest flow:** `data/*.md` → `ingest.py` → `chunk_text()` → `fc.get_embedding()` → `rag.db`

**Query flow:** question → `answer_query()` → `get_top_chunks()` → `rag.db` → `build_user_message()` → `fc.chat()` → answer + sources

---

## Phase 1 — Foundational Learning (Weeks 1–2)

### Week 1: RAG Concepts and Local AI Setup

**Learning objectives:**
- Explain RAG as retrieve → augment → generate
- Understand why retrieved context reduces hallucination
- Install project dependencies and verify Foundry Local
- Run the first local model / catalog check

**Key resources:**
- [What is Foundry Local?](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started/overview)
- [Get started with Foundry Local (Python)](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started/quickstart-python)
- Tech Community blog post linked above

**Hands-on work:**
1. Clone the repo and activate the virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   source .venv/bin/activate       # macOS / Linux
   pip install -r requirements.txt
   ```
2. Run the setup checker: `python check_setup.py`
3. Run the "Hello Model" test — loads the chat model and prints one completion:

   ```bash
   python examples/hello_model.py
   ```

4. Read `data/rag_nedir.md` and `data/foundry_local.md`
5. Role-play RAG manually: one student finds the relevant paragraph,
   another formulates an answer using only that paragraph

**Milestone:** Every team can activate the virtual environment, pass the setup
checker, and run a first local model inference via `examples/hello_model.py`.

---

### Week 2: Embeddings, Vector Search, SQLite, and Prompt Engineering

**Learning objectives:**
- Describe embeddings as numeric representations of text meaning
- Compute cosine similarity conceptually and in code
- Understand why SQLite is a good local store for small document sets
- Write prompts that constrain the model to the supplied context

**Key resources:**
- [Tutorial: Build a RAG application (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/tutorials/tutorial-rag)
- [Prompt engineering techniques (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering)
- `data/embeddings.md`, `data/sqlite.md`, `data/prompt_engineering.md` (this project)

**Hands-on work:**
1. Read `data/embeddings.md`, `data/sqlite.md`, `data/prompt_engineering.md`
2. Run the standalone exercises:

   ```bash
   python examples/embedding_demo.py     # embeddings + cosine similarity in memory
   python examples/sql_sandbox.py        # SQLite basics with the project schema
   ```

3. Inspect `db.py`, `retrieval.py`, and `prompts.py`
4. Add a new `.md` file to `data/` on a topic of your choice
5. Run `python ingest.py` to build `rag.db`
6. Test retrieval: `python retrieval.py "your question here"`

**Milestone:** Teams have a populated SQLite database and can retrieve relevant chunks for a query.

---

## Phase 2 — Project Implementation (Weeks 3–4)

### Week 3: Data Ingestion and Retrieval Pipeline

**Learning objectives:**
- Split documents into useful chunks with overlap
- Store source file names, chunk text, and embedding vectors
- Tune top-k retrieval for a small knowledge base

**Key resources:**
- `ingest.py` and `retrieval.py` (this project)
- `data/rag_pipeline.md` (this project)
- [Microsoft Learn RAG tutorial — Generate document embeddings](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/tutorials/tutorial-rag#generate-document-embeddings)

**Hands-on work:**
1. Read `data/rag_pipeline.md` for a detailed explanation of the two phases
2. Customize the documents in `data/` for your team's topic
3. Adjust `MAX_CHARS` and `OVERLAP` in `ingest.py` if needed
4. Re-run ingestion and test several queries: `python retrieval.py "..."`
5. Record examples where retrieval works well and where it fails

**Milestone:** Each team has a project-specific document collection and a reliable retrieval function.

---

### Week 4: LLM Integration and User Interface

**Learning objectives:**
- Combine retrieved context with a system prompt
- Call the local chat model through `foundry_client.py`
- Compare CLI and Streamlit interfaces

**Key resources:**
- `generation.py`, `prompts.py`, `foundry_client.py` (this project)
- [Foundry Local SDK reference](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/reference/sdk-reference)
- `data/architecture.md` (this project)

**Hands-on work:**
1. Run `python main.py` and ask both answerable and unanswerable questions
2. Run `streamlit run ui_streamlit.py`
3. Enable "Retrieved chunks göster" in the sidebar to see what the model receives
4. Tune `SYSTEM_PROMPT` in `prompts.py` for your domain (language, tone, citation style)
5. Try changing `CHAT_MODEL_ALIAS` in `foundry_client.py` to a different model

**Interface options (choose one):**

| Option | Command | Notes |
|--------|---------|-------|
| CLI | `python main.py` | Simplest; shows sources inline |
| Streamlit | `streamlit run ui_streamlit.py` | Browser UI with debug panel |

**Milestone:** Each team has an end-to-end assistant that retrieves context and generates
a grounded answer from the local model.

---

## Phase 3 — Testing, Evaluation, and Documentation (Weeks 5–6)

### Week 5: System Testing and Evaluation

**Learning objectives:**
- Build a test set with answerable and unanswerable questions
- Evaluate answer quality, missing-information behavior, and response time
- Debug retrieval mistakes separately from generation mistakes

**Key resources:**
- `eval/questions.yaml` and `eval/run_eval.py` (this project)

**Hands-on work:**
1. Update `eval/questions.yaml` with team-specific questions (min. 10 answerable, 4 unanswerable)
2. Run the evaluation:
   ```bash
   python eval/run_eval.py
   python eval/run_eval.py --verbose      # see full answers
   python eval/run_eval.py --fail-only    # see only failures
   ```
3. For each FAIL, decide whether to fix the document, chunk size, top-k, or prompt
4. Check edge cases: empty input, single-word question, very long question

**Common fixes:**

| Problem | Fix |
|---------|-----|
| Retrieval misses obvious answer | Add more detail to the source document |
| Score below 0.45 for valid question | Lower `MIN_RELEVANCE_SCORE` in `generation.py` |
| Model echoes instructions | Adjust `SYSTEM_PROMPT` in `prompts.py` |
| Slow response | Switch to a smaller model alias |

**Milestone:** Teams have documented test results and a short improvement list.

---

### Week 6: Documentation and Demo Day

**Learning objectives:**
- Explain the project architecture clearly to a non-technical audience
- Document setup and usage so another student can run it from scratch
- Present a live demo with realistic questions

**Hands-on work:**
1. Update `README.md` with any team-specific setup notes
2. Clean up debug output and add comments to key functions
3. Prepare a 5-minute demo script — use
   [`docs/presentation_outline.md`](presentation_outline.md) as the template
   (Problem Statement, Key Features & Components, Live Demo, Lessons Learned):
   - Show the `data/` folder and explain what the documents cover
   - Ask a question the assistant can answer — show sources
   - Ask a question it should reject — show the fallback message
   - Toggle the "Retrieved chunks" panel to explain retrieval
4. Rehearse the demo at least once on the target machine

**Milestone:** Final demo is rehearsed, documentation is complete, and the assistant is
ready to run on the presentation machine.

---

## Quick Command Reference

```bash
# First-time setup
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python check_setup.py           # verify installation
python check_setup.py --models  # list available model aliases

# Build the knowledge base (run whenever data/ changes)
python ingest.py

# Run the assistant
python main.py                         # CLI
streamlit run ui_streamlit.py          # web UI

# Test a single retrieval
python retrieval.py "your question"

# Evaluate
python eval/run_eval.py
python eval/run_eval.py --verbose
python eval/run_eval.py --fail-only
```

---

## Definition of Done

- [x] `python check_setup.py` passes with no errors
- [x] `python ingest.py` builds `rag.db` with chunks from `data/`
- [x] `python main.py` accepts questions and returns grounded answers with sources
- [x] If an answer is not in the documents, the assistant says so (no hallucination)
- [x] `python eval/run_eval.py` has been run and results are recorded in `eval/results.md`
- [x] README is updated with any team-specific notes
- [ ] Final demo rehearsed and working on the presentation machine
