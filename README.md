<div align="center">

# 🧠 Local RAG Assistant

### Fully offline document Q&A — no cloud, no API keys, no internet

**Python · Foundry Local · SQLite · Streamlit**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Foundry Local](https://img.shields.io/badge/Foundry_Local-on--device-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)](https://learn.microsoft.com/azure/ai-foundry/foundry-local/)
[![SQLite](https://img.shields.io/badge/SQLite-vector_store-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

[![Offline](https://img.shields.io/badge/100%25-offline-2EA043?style=flat-square&logo=wifi&logoColor=white)](#-why-local)
[![Eval](https://img.shields.io/badge/eval-22%2F26_passing-2EA043?style=flat-square&logo=checkmarx&logoColor=white)](#-evaluation)
[![Knowledge Base](https://img.shields.io/badge/knowledge_base-7_docs_·_55_chunks-8957E5?style=flat-square&logo=databricks&logoColor=white)](#-data-model)
[![Languages](https://img.shields.io/badge/answers-TR_%2F_EN-F1502F?style=flat-square&logo=googletranslate&logoColor=white)](#-design-decisions)
[![License](https://img.shields.io/badge/license-MIT-D4A72C?style=flat-square&logo=opensourceinitiative&logoColor=white)](#-license)
[![Platform](https://img.shields.io/badge/platform-Windows_·_Apple_Silicon-555555?style=flat-square&logo=windows&logoColor=white)](#prerequisites)

</div>

---

## 📖 What is this?

This assistant answers questions **only from your own local documents**. It finds the most
relevant passages, injects them into the prompt, and asks an on-device model to write a
source-grounded answer. If the documents don't contain the answer, it says so instead of
making one up.

Everything — the embedding model, the chat model, and the database — runs on your own
machine. After the first model download, you can pull the network cable.

> [!NOTE]
> **Reference article:** [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968) · **Teaching plan:** [`docs/one_month_plan.md`](docs/one_month_plan.md)

---

## 🏗️ Architecture

A five-layer design where **every arrow stays inside the machine**.

```mermaid
flowchart TD
    subgraph CLIENT["🖥️ &nbsp;CLIENT LAYER"]
        UI["ui_streamlit.py<br/><i>web UI + debug panel</i>"]
        CLI["main.py<br/><i>terminal Q&A loop</i>"]
    end

    subgraph APP["⚙️ &nbsp;APPLICATION LAYER"]
        GEN["generation.answer_query()<br/><i>orchestration + guardrails</i>"]
        PRM["prompts.build_user_message()<br/><i>system prompt + context</i>"]
    end

    subgraph RET["🔍 &nbsp;RETRIEVAL LAYER"]
        TOP["retrieval.get_top_chunks()<br/><i>cosine similarity · top-K</i>"]
        ING["ingest.py<br/><i>chunk → embed → store</i>"]
    end

    subgraph DATA["💾 &nbsp;DATA LAYER"]
        DB[("rag.db<br/><i>SQLite · 55 chunks</i>")]
        FILES["data/*.md<br/><i>7 knowledge docs</i>"]
    end

    subgraph AI["🤖 &nbsp;AI LAYER — on device"]
        FC["foundry_client.py<br/><i>single SDK touch point</i>"]
        CHATM["qwen2.5-1.5b<br/><i>chat</i>"]
        EMBM["qwen3-embedding-0.6b<br/><i>embedding</i>"]
    end

    UI --> GEN
    CLI --> GEN
    GEN --> PRM
    GEN --> TOP
    TOP --> DB
    FILES --> ING
    ING --> DB
    ING -.embed.-> FC
    TOP -.embed query.-> FC
    GEN -.generate.-> FC
    FC --> CHATM
    FC --> EMBM

    classDef client fill:#DBEAFE,stroke:#2563EB,stroke-width:2px,color:#1E3A8A
    classDef app fill:#EDE9FE,stroke:#7C3AED,stroke-width:2px,color:#4C1D95
    classDef ret fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    classDef data fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    classDef ai fill:#FFE4E6,stroke:#E11D48,stroke-width:2px,color:#881337

    class UI,CLI client
    class GEN,PRM app
    class TOP,ING ret
    class DB,FILES data
    class FC,CHATM,EMBM ai
```

> [!TIP]
> **The `foundry_client.py` rule:** it is the *only* file that imports the Foundry SDK.
> If the SDK changes, exactly one file needs updating.

---

## 🔄 How a question becomes an answer

UML sequence of a single query — from keystroke to cited answer.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant G as generation
    participant R as retrieval
    participant DB as rag.db
    participant F as foundry_client
    participant M as Local Models

    User->>G: answer_query("Cosine similarity nedir?")
    activate G

    G->>R: get_top_chunks(question, k=3)
    activate R
    R->>F: get_embedding(question)
    F->>M: embed
    M-->>F: vector
    F-->>R: query vector
    R->>DB: SELECT source, content, embedding
    DB-->>R: 55 stored chunks
    Note over R: cosine(query, chunk) for all 55<br/>sort desc → take top 3
    R-->>G: [{text, source, score}, ...]
    deactivate R

    alt top score < 0.45 — off-topic
        G-->>User: ⛔ "Bu konuda elimdeki dökümanlarda bilgi yok."
    else top score ≥ 0.45 — relevant
        G->>F: chat(system prompt + CONTEXT + QUESTION)
        F->>M: generate (temp 0.2, max 256 tok)
        M-->>F: raw answer
        F-->>G: answer text
        Note over G: guardrails: echo check · refusal check
        G-->>User: ✅ answer + [kaynak: dosya.md]
    end
    deactivate G
```

---

## 🛡️ The guardrail gate

The part that keeps the assistant honest. A small on-device model will sometimes echo its
own instructions or give up on a question it *can* answer — both are handled explicitly.

```mermaid
flowchart TD
    Q(["❓ Question"]) --> EMPTY{"empty?"}
    EMPTY -->|yes| ASK["📝 'Lütfen bir soru yazın.'"]
    EMPTY -->|no| RET["🔍 retrieve top-3"]
    RET --> GATE{"top score<br/>≥ 0.45 ?"}
    GATE -->|no| FB["⛔ 'Bu konuda ... bilgi yok.'<br/><i>honest refusal</i>"]
    GATE -->|yes| LLM["🤖 ask the model"]
    LLM --> ECHO{"echoed the<br/>instructions?"}
    ECHO -->|yes| PASS["📄 show best passage<br/>+ its source"]
    ECHO -->|no| REF{"short refusal<br/>≤ 120 chars?"}
    REF -->|no| OK["✅ answer + sources"]
    REF -->|yes| STRONG{"top score<br/>≥ 0.60 ?"}
    STRONG -->|yes| PASS
    STRONG -->|no| FB

    classDef good fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    classDef stop fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#7F1D1D
    classDef mid fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    classDef node fill:#E0F2FE,stroke:#0284C7,stroke-width:2px,color:#0C4A6E

    class OK,PASS good
    class FB,ASK stop
    class GATE,ECHO,REF,STRONG,EMPTY mid
    class Q,RET,LLM node
```

> [!IMPORTANT]
> A refusal is **respected**, not overwritten — unless retrieval was very strong
> (`score ≥ 0.60`), where giving up is a model failure, not a missing document.
> In that case the best passage is shown verbatim with its source. Nothing is ever invented.

---

## 📥 Ingestion pipeline

Run once, and again whenever `data/` changes.

```mermaid
flowchart LR
    A["📄 data/*.md<br/>7 files"] --> B["✂️ chunk_text()<br/>paragraph split"]
    B --> C{"paragraph<br/>> 800 chars?"}
    C -->|yes| D["🪟 sliding window<br/>800 / overlap 100"]
    C -->|no| E["keep as is"]
    D --> F{"piece<br/>< 150 chars?"}
    E --> F
    F -->|yes| G["🔗 merge with neighbor<br/><i>headings carry no info alone</i>"]
    F -->|no| H["📦 final chunk"]
    G --> H
    H --> I["🧮 get_embedding()"]
    I --> J[("💾 rag.db<br/>55 rows")]

    classDef src fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    classDef proc fill:#EDE9FE,stroke:#7C3AED,stroke-width:2px,color:#4C1D95
    classDef dec fill:#DBEAFE,stroke:#2563EB,stroke-width:2px,color:#1E3A8A
    classDef out fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D

    class A src
    class B,D,E,G,H,I proc
    class C,F dec
    class J out
```

---

## 🗄️ Data model

One table. Embeddings are stored as JSON text — trivially inspectable, no extension needed.

```mermaid
erDiagram
    DOCUMENTS {
        INTEGER id PK "AUTOINCREMENT"
        TEXT    source   "origin file, e.g. sqlite.md"
        TEXT    content  "the chunk text itself"
        TEXT    embedding "JSON-serialized float vector"
    }
```

| Source file | Chunks | Topic |
|-------------|:------:|-------|
| `foundry_local.md` | 10 | Installation, model management, hardware support |
| `rag_pipeline.md` | 10 | Ingestion and query phases, step by step |
| `prompt_engineering.md` | 9 | System/user prompts, RAG prompt design, pitfalls |
| `architecture.md` | 8 | This project's five-layer local architecture |
| `embeddings.md` | 7 | Embeddings, cosine similarity, top-K retrieval |
| `rag_nedir.md` | 6 | RAG overview, hallucination, three-step pipeline |
| `sqlite.md` | 5 | SQLite overview, schema, SQL operations, limits |
| **Total** | **55** | |

---

## 🧩 Module contract

Each module exposes a narrow, stable surface. UML class view:

```mermaid
classDiagram
    direction LR

    class foundry_client {
        <<AI gateway>>
        +CHAT_MODEL_ALIAS str
        +EMBEDDING_MODEL_ALIAS str
        +TEMPERATURE float
        +MAX_TOKENS int
        +warm_up() None
        +get_embedding(text) list~float~
        +chat(messages) str
        +shutdown() None
    }

    class db {
        <<persistence>>
        +get_connection() Connection
        +init_db(conn) None
        +insert_chunk(conn, source, content, emb) None
        +fetch_all_chunks(conn) list~dict~
        +count_by_source(conn) dict
    }

    class retrieval {
        <<search>>
        -_cosine(a, b) float
        +get_top_chunks(query, k) list~dict~
    }

    class generation {
        <<orchestration>>
        +TOP_K int
        +MIN_RELEVANCE_SCORE float
        +STRONG_SCORE float
        +answer_query(question) dict
    }

    class prompts {
        <<templating>>
        +SYSTEM_PROMPT str
        +build_user_message(question, chunks) str
    }

    class ingest {
        <<one-time job>>
        +chunk_text(text) list~str~
        +ingest() None
    }

    generation --> retrieval : top chunks
    generation --> prompts : build message
    generation --> foundry_client : chat
    retrieval --> db : read vectors
    retrieval --> foundry_client : embed query
    ingest --> db : write chunks
    ingest --> foundry_client : embed chunks
```

<details>
<summary><b>📜 Interface contract (copy-paste reference)</b></summary>

```python
# foundry_client.py — the only file that touches the Foundry SDK
foundry_client.warm_up()                        -> None
foundry_client.get_embedding(text: str)         -> list[float]
foundry_client.chat(messages: list[dict])       -> str
foundry_client.shutdown()                       -> None

# retrieval.py
retrieval.get_top_chunks(query: str, k: int = 3) -> list[dict]
# [{"text": str, "source": str, "score": float}, ...]

# generation.py
generation.answer_query(question: str)          -> dict
# {"answer": str, "sources": list[str], "used_chunks": list[dict]}
```

</details>

---

## ⚡ Quick Start

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| 🐍 Python 3.10+ | 3.11 recommended |
| 💻 Windows or Apple Silicon Mac | Intel Mac is not supported by Foundry Local |
| 💽 ~4 GB free disk | Model download, first run only |
| 🌐 Internet | First run only — models are cached afterwards |

### Setup

```bash
# 1 — virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# 2 — dependencies
pip install -r requirements.txt

# 3 — verify environment, catalog, aliases, data and DB
python check_setup.py
python check_setup.py --models  # list every available model alias

# 4 — "Hello Model" smoke test
python examples/hello_model.py
```

### Run

```bash
python ingest.py                # 1️⃣  build the knowledge base
python main.py                  # 2️⃣  terminal interface
streamlit run ui_streamlit.py   # 2️⃣  …or the web UI
```

Drop your own `.txt` / `.md` files into `data/` and rerun `python ingest.py`.

> [!WARNING]
> `ingest.py` **clears and rebuilds** the `documents` table on every run. There is no
> incremental ingestion — fine at 7 documents, wasteful for a large corpus.

<details>
<summary><b>🔧 Model alias mismatch?</b></summary>

If `check_setup.py` reports a missing alias, edit the top of `foundry_client.py`:

```python
CHAT_MODEL_ALIAS      = "qwen2.5-1.5b"          # or: qwen2.5-0.5b, phi-3.5-mini
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
```

Verify what your machine actually has with `foundry model list`.

</details>

---

## 🎛️ Configuration

Every tunable constant lives at the top of its own file.

| Constant | File | Default | Effect |
|----------|------|:-------:|--------|
| `CHAT_MODEL_ALIAS` | `foundry_client.py` | `qwen2.5-1.5b` | Model that writes the answer |
| `EMBEDDING_MODEL_ALIAS` | `foundry_client.py` | `qwen3-embedding-0.6b` | Model that vectorizes text |
| `TEMPERATURE` | `foundry_client.py` | `0.2` | Answer randomness — low = factual |
| `MAX_TOKENS` | `foundry_client.py` | `256` | Answer length ceiling |
| `TOP_K` | `generation.py` | `3` | Chunks pulled per query |
| `MIN_RELEVANCE_SCORE` | `generation.py` | `0.45` | Below this → honest refusal |
| `STRONG_SCORE` | `generation.py` | `0.60` | Above this → trust retrieval over a model give-up |
| `MAX_CHARS` | `ingest.py` | `800` | Target chunk size |
| `OVERLAP` | `ingest.py` | `100` | Overlap when splitting a long paragraph |
| `MIN_CHARS` | `ingest.py` | `150` | Shorter pieces merge with their neighbor |

---

## 🧪 Evaluation

```bash
python eval/run_eval.py              # all 26 questions
python eval/run_eval.py --verbose    # print full answers
python eval/run_eval.py --fail-only  # only the failures
```

Every run writes a persistent report to [`eval/results.md`](eval/results.md) — per-question
PASS/FAIL, timing and cited sources.

<div align="center">

| Category | Count | Result | What it checks |
|----------|:-----:|:------:|----------------|
| 🟢 Answerable | 18 | 14 ✅ / 4 ❌ | Answers from the docs and cites the source |
| 🔵 Unanswerable | 4 | 4 ✅ | Refuses instead of hallucinating |
| 🟣 Edge cases | 4 | 4 ✅ | Empty, one-word, vague, very long — no crash |
| **Total** | **26** | **22 / 26 · 85%** | avg **44.5 s** per question, CPU-only laptop |

</div>

<details>
<summary><b>🔎 Known weak spots &amp; the improvement list</b></summary>

- **Keyword grading is too strict.** The 1.5B model paraphrases instead of using the literal
  expected token — it explains hardware acceleration without the word *"GPU"*, or describes
  the threshold without quoting *"0.45"*. All 4 failures are of this kind.
  → *Next:* accept multiple keywords per question, or grade with a second model pass.
- **Rare refusal on an answerable question** (run-to-run variance even at `TEMPERATURE=0.2`).
  The `STRONG_SCORE` passage fallback covers most of these.
  → *Next:* retry once on refusal.
- **Larger merged chunks improved grounding but raised latency** on CPU.
  → *Next:* trim to top-2 chunks for short questions, or run on NPU/GPU.

</details>

---

## 🧭 Design decisions

<table>
<tr><td width="34%"><b>🔢 Brute-force cosine, no vector DB</b></td>
<td>For a 5–10 document corpus, comparing the query vector against all 55 stored vectors in
pure Python is fast and needs zero extra dependencies. A vector index only pays off in the
thousands.</td></tr>

<tr><td><b>💾 Plain <code>sqlite3</code></b></td>
<td>Single file, serverless, cross-platform — the right shape for a single-user local app.
Embeddings as JSON text keep the DB inspectable with any SQLite browser.</td></tr>

<tr><td><b>✂️ Paragraph-based chunking</b></td>
<td>Paragraphs keep semantic units intact; the 100-char overlap prevents context loss when a
long paragraph is split mid-thought. Sub-150-char pieces merge upward so bare headings can't
win retrieval while carrying no information.</td></tr>

<tr><td><b>🎯 <code>TOP_K=3</code> with a relevance gate</b></td>
<td>Off-topic questions fall below <code>0.45</code> and get an honest "I don't have that"
instead of a fabrication — the single most important behavior in the system.</td></tr>

<tr><td><b>🐇 Small models, measured</b></td>
<td>On this project's test machine <code>qwen2.5-0.5b</code> was faster but too weak in
Turkish, and <code>phi-3.5-mini</code> took ~2 min/answer on CPU. <code>qwen2.5-1.5b</code> is
the measured sweet spot. Both models warm up at startup, so the first question is as fast as
the rest.</td></tr>
</table>

### Limitations

- Answer depth is bounded by a ~1.5B on-device model — subtle multi-step reasoning stays shallow.
- No incremental ingestion; the table is rebuilt on every run.
- Brute-force retrieval scales linearly with chunk count.
- SQLite here is single-user — no concurrent writers.
- Foundry Local does not support Intel Macs.
- Bilingual prompting can occasionally produce mixed-language answers with very small models.

---

## 📂 Project layout

```text
rag-assistant/
├── 🤖 foundry_client.py     # the ONLY Foundry SDK touch point
├── 💾 db.py                 # SQLite schema + helpers
├── 📥 ingest.py             # read → chunk → embed → store
├── 🔍 retrieval.py          # embed query → cosine → top-K
├── 💬 prompts.py            # system prompt + context builder
├── ⚙️ generation.py         # answer_query() pipeline + guardrails
├── 🖥️ main.py               # CLI Q&A loop
├── 🎨 ui_streamlit.py       # web UI with sidebar + debug panel
├── ✅ check_setup.py        # environment / catalog / data / DB checker
├── 📊 eval/
│   ├── questions.yaml       # 26 test questions
│   ├── run_eval.py          # runner with timing + report writer
│   └── results.md           # recorded run
├── 🎓 examples/
│   ├── hello_model.py       # week 1 — runtime smoke test
│   ├── embedding_demo.py    # week 2 — embeddings + cosine in memory
│   └── sql_sandbox.py       # week 2 — SQLite with the project schema
├── 📚 docs/
│   ├── one_month_plan.md
│   ├── week_by_week_schedule.md
│   └── presentation_outline.md
└── 📄 data/*.md             # 7 knowledge base documents
```

---

## 🔒 Why local?

<div align="center">

| | Cloud RAG | **This project** |
|---|---|---|
| 🌐 Internet | required per query | first download only |
| 🔑 API keys | required | none |
| 💰 Cost per query | metered | zero |
| 🗝️ Where your documents go | a vendor's servers | **your disk** |
| ⏱️ Latency | network round trip | local compute |

</div>

---

## ✅ Definition of Done

- [x] `python check_setup.py` passes with no errors
- [x] `python ingest.py` creates chunks in `rag.db`
- [x] CLI and Streamlit both return grounded answers with sources
- [x] Unanswerable questions get a fallback response — no hallucination
- [x] `python eval/run_eval.py` runs and results are recorded in `eval/results.md`
- [x] `README.md` documents architecture, decisions and limitations
- [ ] Final demo rehearsed on the target machine

---

## 📄 License

MIT — a teaching sample built for learning and experimentation.

<div align="center">
<br/>
<sub>Built to run entirely on your own machine. 🔌</sub>
</div>
