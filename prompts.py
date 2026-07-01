"""
prompts.py  —  System prompt + bağlam şablonu
"""
from __future__ import annotations

SYSTEM_PROMPT = """You are a local document assistant. You answer questions using ONLY the
information provided in the CONTEXT section below.

Rules:
1. Use ONLY the information in the CONTEXT. Do not add knowledge from outside the context.
2. If the context does not contain a sufficient answer, reply with exactly:
   "Bu konuda elimdeki dökümanlarda bilgi yok."
   Do not guess, do not make up information.
3. Keep your answer concise and to the point.
4. Always cite the source file name in your answer, for example: [kaynak: dosya.md]
5. If the user writes in Turkish, answer in Turkish. If in English, answer in English."""


def build_user_message(question: str, chunks: list[dict]) -> str:
    """Getirilen parçaları BAĞLAM olarak biçimleyip soruyla birleştirir."""
    if chunks:
        blocks = [f"[kaynak: {c['source']}]\n{c['text']}" for c in chunks]
        context = "\n\n---\n\n".join(blocks)
    else:
        context = "(ilgili bağlam bulunamadı)"
    return f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer:"
