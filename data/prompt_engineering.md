# Prompt Engineering for RAG

## What is Prompt Engineering?

Prompt engineering is the practice of carefully designing the input text sent to a language model in order to get the best possible output. In a RAG system, good prompts are what turn retrieved chunks into useful, accurate answers.

## System Prompts and User Prompts

Modern chat models accept a list of messages, each with a role:

- system: high-level instructions that define the assistant's behavior and constraints
- user: the human's question in the current turn
- assistant: the model's previous replies in a multi-turn conversation

In this project, the system prompt tells the model to answer only from the supplied context and to cite its sources. The user message contains the retrieved chunks followed by the question.

## Key Principles for RAG Prompts

**Ground the model in the context.** The system prompt must explicitly tell the model to use only the provided context. Without this instruction small models tend to mix training knowledge with the retrieved text.

**Handle missing information gracefully.** Tell the model what to say when the context does not contain the answer. A phrase like "if the answer is not in the context, say you do not have that information" prevents the model from guessing.

**Be concise.** Short, direct prompts reduce the risk of the model being confused by contradictory instructions. Leave detailed formatting instructions out unless the application requires them.

**Cite sources.** Ask the model to include the source file name in its answer. This lets users verify the information and builds trust in the assistant.

## Example System Prompt

"You are an assistant that answers questions based only on the provided context. If the context does not contain the answer, say you do not have that information. Always include the source file name in your answer."

## Context Formatting

When multiple chunks are retrieved they should be clearly separated in the prompt. A common format is:

[source: filename.md]
chunk text here

---

[source: other_file.md]
second chunk text here

QUESTION: the user's question

Answer:

## What to Avoid

Do not use vague role descriptions such as "you are a helpful assistant". For RAG tasks the model needs to know it is constrained to the provided context. Vague descriptions lead to hallucinated answers that sound plausible but are not grounded in the documents.
