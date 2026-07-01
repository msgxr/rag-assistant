# SQLite: Local Data Storage for RAG

## What is SQLite?

SQLite is a serverless, self-contained relational database engine. Unlike MySQL or PostgreSQL, SQLite does not run as a separate server process. The entire database is a single file on disk. This makes it ideal for local applications that need persistent storage without infrastructure complexity.

SQLite is the most widely deployed database engine in the world. It is built into Python, iOS, Android, and most operating systems. No installation is required beyond the standard library.

## Why SQLite for This Project?

In a RAG system you need to store document chunks and their embedding vectors persistently. SQLite is the right choice here because:

The database is a single file (rag.db) that lives in the project folder. You can delete it and rebuild it at any time by running python ingest.py.

Python includes the sqlite3 module in the standard library. No extra package is required.

For a few hundred or even a few thousand document chunks, SQLite with in-memory cosine similarity comparison is fast enough. Retrieval completes in milliseconds.

## Schema Used in This Project

The documents table has four columns:

- id: integer primary key, auto-incremented
- source: the file name of the document the chunk came from
- content: the text of the chunk
- embedding: the embedding vector stored as a JSON-serialized list of numbers

## Basic SQL Operations

To count how many chunks are stored:

    SELECT COUNT(*) FROM documents;

To inspect the first few chunks:

    SELECT id, source, substr(content, 1, 80) FROM documents LIMIT 5;

To delete all rows and start fresh:

    DELETE FROM documents;

## Limitations

SQLite does not have built-in vector similarity functions. Cosine similarity in this project is computed in Python after fetching all rows. This is efficient for small datasets. For datasets with tens of thousands of chunks a dedicated vector database such as Chroma or Qdrant would give better performance.

SQLite is not designed for high-concurrency writes. For this single-user local assistant that limitation does not matter.
