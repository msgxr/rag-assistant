"""
generation.py  —  answer_query(question)  (Sahip: ŞEYMA)
Bağlamı retrieval'dan çeker, promptu kurar, Foundry chat ile cevabı üretir.
"""
from __future__ import annotations

import foundry_client as fc
import prompts
from retrieval import get_top_chunks

TOP_K = 3


def answer_query(question: str) -> dict:
    """
    Uçtan uca cevap.
    -> {"answer": str, "sources": list[str], "used_chunks": list[dict]}
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Lütfen bir soru yazın.", "sources": [], "used_chunks": []}

    chunks = get_top_chunks(question, k=TOP_K)

    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {"role": "user", "content": prompts.build_user_message(question, chunks)},
    ]
    answer = fc.chat(messages)

    sources: list[str] = []
    for c in chunks:
        if c["source"] not in sources:
            sources.append(c["source"])

    return {"answer": answer.strip(), "sources": sources, "used_chunks": chunks}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Bu sistem ne işe yarar?"
    r = answer_query(q)
    print("CEVAP:\n", r["answer"])
    print("\nKAYNAKLAR:", ", ".join(r["sources"]) or "—")
