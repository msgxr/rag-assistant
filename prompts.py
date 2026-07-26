"""
prompts.py  —  System prompt + bağlam şablonu
"""
from __future__ import annotations

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about local documents.
The CONTEXT below was retrieved because it is relevant to the question.
Read it carefully and answer the QUESTION using the information in it.

Rules:
1. Base your answer only on the CONTEXT. Do not use outside knowledge.
2. Answer in the same language as the question (Turkish question -> Turkish answer).
3. Be concise: one to three sentences are enough.
4. End your answer with the source file name, for example: [kaynak: dosya.md]
5. Only if the context has nothing to do with the question, reply:
   "Bu konuda elimdeki dökümanlarda bilgi yok." Do not guess."""


def build_user_message(question: str, chunks: list[dict]) -> str:
    """Getirilen parçaları BAĞLAM olarak biçimleyip soruyla birleştirir."""
    if chunks:
        blocks = [f"[kaynak: {c['source']}]\n{c['text']}" for c in chunks]
        context = "\n\n---\n\n".join(blocks)
    else:
        context = "(ilgili bağlam bulunamadı)"
    return (f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\n"
            "Answer (use the same language as the QUESTION):")
