# Embeddings and Vector Search

## What is an Embedding?

An embedding is a numeric vector that represents the meaning of a piece of text. Words or sentences with similar meanings produce vectors that are close to each other in vector space. This property makes embeddings useful for semantic search.

For example, the sentences "How do I install Foundry Local?" and "What are the installation steps for Foundry Local?" will have very similar embeddings even though they use different words.

## How Embeddings Work in RAG

In a RAG pipeline, embeddings are used in two stages:

1. At ingestion time, each document chunk is converted to an embedding vector and stored alongside the text in the database.
2. At query time, the user question is also converted to an embedding vector and compared against all stored vectors.

The comparison uses cosine similarity: a score between 0 and 1 where 1 means the two vectors are identical and 0 means they share no direction.

## Cosine Similarity

Cosine similarity measures the angle between two vectors. If the angle is small the vectors point in the same direction and the texts are semantically similar. The formula is:

cosine_similarity(A, B) = (A · B) / (|A| * |B|)

In Python this can be computed with a simple loop over the vector elements. For small document collections (a few hundred chunks) brute force comparison is fast enough.

## Embedding Models

Embedding models are separate from chat models. They are smaller and faster. Their only job is to convert text to a vector. In this project the embedding model alias is configured in foundry_client.py as qwen3-embedding-0.6b by default. The embedding model is loaded once and reused for all chunks during ingestion and for each query at runtime.

## Top-K Retrieval

After scoring all chunks by cosine similarity with the query, the retrieval function returns the K chunks with the highest scores. K is set to 3 in this project. These three chunks are then injected into the prompt as context for the chat model.
