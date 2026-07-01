# Foundry Local: Setup and Model Management

## Installation

Foundry Local is installed as a Python package. On Windows the package is foundry-local-sdk-winml. On macOS and Linux the package is foundry-local-sdk. The import name is the same on all platforms: foundry_local_sdk.

In this project the correct package is selected automatically by requirements.txt based on the operating system.

## Checking Available Models

After installing the SDK you can see all models available in the local catalog by running:

    python check_setup.py --models

This prints a table of model aliases, their capabilities, and their context lengths. You do not need an internet connection after the first catalog download.

## Downloading a Model

Models are downloaded on first use. The Foundry Local runtime handles the download automatically when you call model.load() or when the application first calls the embedding or chat function. The download requires an internet connection. After the model is cached on disk no internet connection is needed.

Chat models are several gigabytes in size. The default model qwen2.5-0.5b is one of the smallest options and downloads quickly. The phi-3.5-mini model gives higher quality answers but is larger.

## Switching Models

To use a different model, change the CHAT_MODEL_ALIAS constant in foundry_client.py. Use the alias shown by check_setup.py --models. Common options include:

- qwen2.5-0.5b: fast, small, good for development
- phi-3.5-mini: higher quality, slower on CPU
- phi-4-mini: best quality among small models, requires more RAM

The embedding model alias is EMBEDDING_MODEL_ALIAS. Do not change the embedding model after running ingestion unless you also delete rag.db and rerun python ingest.py. The chat and embedding models must be consistent.

## Hardware Requirements

Foundry Local runs on CPU without a GPU. Performance is faster with a dedicated GPU or NPU. On a modern laptop with 16 GB of RAM the default chat model produces answers in one to three seconds per query.

Apple Silicon Macs use the Metal GPU backend automatically. Intel Macs are not supported by the macOS package. On Intel Macs, use the project on Windows or Linux instead.

## Unloading Models

When the application exits, foundry_client.shutdown() is called to release model memory. This function is optional but recommended for scripts that run briefly, such as the CLI in main.py.
