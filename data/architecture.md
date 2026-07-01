# Project Architecture

## Components

This project runs entirely on a single machine. There is no cloud service, no external API, and no internet connection required after models are downloaded.

The project has five logical layers.

### Client Layer

Two interfaces are provided. The CLI in main.py reads questions from the terminal in a loop and prints answers. The web UI in ui_streamlit.py provides a browser-based chat interface with an optional debug panel that shows retrieved chunks.

The data/ folder is not a runtime component. It holds the source documents that are processed during ingestion.

### Application Layer

generation.py contains the answer_query function which is the single entry point for both the CLI and the Streamlit UI. It calls retrieval to get context chunks, calls prompts to build the message list, calls the chat model, and applies quality checks on the returned answer.

prompts.py contains the system prompt and the function that assembles retrieved chunks into the user message. Separating prompts from generation logic makes it easy to experiment with different instructions without touching the retrieval or model code.

### RAG Retrieval Layer

ingest.py reads documents from data/, splits them into chunks, embeds each chunk, and stores the results in rag.db.

retrieval.py embeds the user query and computes cosine similarity against every stored chunk. It returns the top K chunks sorted by score.

### Data Layer

db.py defines the SQLite schema and provides helper functions for connecting, inserting, and fetching data. The documents table has four columns: id, source, content, and embedding. The embedding is stored as a JSON-serialized list of floats.

rag.db is the SQLite database file. It is created by running python ingest.py.

The eval/ directory contains a YAML file with test questions and a runner script.

### AI Layer

foundry_client.py is the only file in the project that imports the Foundry Local SDK. All other modules call foundry_client.chat or foundry_client.get_embedding. This single integration point means only one file needs to change if the SDK version changes.

Foundry Local runs the chat model and the embedding model on the local device using CPU or NPU acceleration. No internet connection is needed during inference.

## Data Flow

User question -> answer_query() -> get_top_chunks() -> SQLite -> top K chunks -> build_user_message() -> fc.chat() -> answer string -> return to UI

Ingestion flow: data/*.md -> ingest.py -> chunk_text() -> fc.get_embedding() -> db.insert_chunk() -> rag.db

## Configuration

The only file that needs to be edited after installation is foundry_client.py. It contains two constants:

CHAT_MODEL_ALIAS is the alias of the model used for generating answers.
EMBEDDING_MODEL_ALIAS is the alias of the model used for creating and comparing vectors.

Run python check_setup.py --models to see all aliases available on your machine.
