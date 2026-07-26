# RAG Pipeline: How It Works End to End

## Overview

A RAG pipeline has two distinct phases: ingestion and query. These two phases run at different times and serve different purposes.

## Özet (Türkçe)

ingest.py scripti data/ klasöründeki .txt ve .md dosyalarını okur, metinleri
parçalara (chunk) böler, her parça için bir embedding vektörü üretir ve
sonuçları rag.db veritabanındaki documents tablosuna kaydeder.

Varsayılan chunk boyutu 800 karakterdir ve ardışık parçalar arasında 100
karakterlik örtüşme (overlap) vardır. Örtüşme, parça sınırındaki cümlelerin
kaybolmasını önler.

Sorgu anında kullanıcının sorusu aynı embedding modeliyle vektöre çevrilir,
cosine similarity ile en alakalı 3 parça bulunur ve bu parçalar bağlam olarak
yerel chat modeline verilir. En iyi parçanın skoru 0.45'in altındaysa asistan
cevap uydurmak yerine bilgi olmadığını söyler.

## Ingestion Phase

Ingestion happens before the assistant is used. It reads documents, splits them into chunks, converts each chunk to an embedding, and stores everything in the database. In this project ingestion is triggered by running:

    python ingest.py

The steps are:

1. Read every .txt and .md file from the data/ folder.
2. Split the text into chunks. The default chunk size is 800 characters with 100 characters of overlap between consecutive chunks. The overlap ensures that sentences at the boundary of a chunk are not lost.
3. Call the embedding model once per chunk to get a vector.
4. Insert the chunk text, the source file name, and the vector into the SQLite database as a row in the documents table.

Ingestion clears the documents table before inserting new rows. This means you can safely rerun the script after editing or adding documents.

## Query Phase

The query phase runs every time a user asks a question. The steps are:

1. Receive the user's question as a string.
2. Embed the question using the same embedding model used during ingestion.
3. Fetch all rows from the documents table and compute cosine similarity between the question embedding and each stored chunk embedding.
4. Return the top 3 chunks by similarity score.
5. Build a prompt that includes the retrieved chunks as context and the user question.
6. Send the prompt to the local chat model and return the answer.

The minimum similarity score required to use a chunk is 0.45. If the best chunk scores below this threshold, the assistant returns a fallback message saying it does not have information on that topic.

## Why Split Into Chunks?

Language models have a limited context window. You cannot feed an entire document into the prompt. Splitting into chunks lets you select only the most relevant passages. Smaller chunks also make similarity search more precise because a chunk covering one specific topic will match a related question more strongly than a large block of mixed content.

## Chunking Strategy in This Project

The ingest.py script first splits text on blank lines to get natural paragraphs. If a paragraph is shorter than 800 characters it is kept as one chunk. If a paragraph is longer it is split with a sliding window of 800 characters and 100 characters of overlap. Very short paragraphs such as headings or single code lines are merged with the neighboring paragraph, because a chunk that contains only a heading carries no information and can mislead the similarity search. This approach preserves sentence context while keeping chunk sizes manageable.
