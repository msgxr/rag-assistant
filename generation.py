"""
generation.py  —  answer_query(question)
Bağlamı retrieval'dan çeker, promptu kurar, Foundry chat ile cevabı üretir.
"""
from __future__ import annotations

import foundry_client as fc
import prompts
from retrieval import get_top_chunks

TOP_K = 3
MIN_RELEVANCE_SCORE = 0.45
FALLBACK_ANSWER = "Bu konuda elimdeki dökümanlarda bilgi yok."
BAD_ANSWER_MARKERS = [
    "bilgi yok",
    "bağlamda cevap",
    "baglamda cevap",
    "aynen şunu yaz",
    "aynen sunu yaz",
    "context does not",
    "not in the context",
]


def _top_score(chunks: list[dict]) -> float:
    if not chunks:
        return 0.0
    return float(chunks[0].get("score", 0.0))


def _looks_like_bad_answer(answer: str) -> bool:
    text = answer.lower()
    return any(marker in text for marker in BAD_ANSWER_MARKERS)


def _context_answer(chunks: list[dict]) -> str:
    """
    Small local chat models can occasionally echo the instructions instead of
    answering. When retrieval is strong, fall back to the best retrieved chunk.
    """
    if not chunks:
        return FALLBACK_ANSWER

    best = chunks[0]
    text = " ".join(str(best["text"]).split())
    return f"{text} [kaynak: {best['source']}]"


def answer_query(question: str) -> dict:
    """
    Uçtan uca cevap.
    -> {"answer": str, "sources": list[str], "used_chunks": list[dict]}
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Lütfen bir soru yazın.", "sources": [], "used_chunks": []}

    chunks = get_top_chunks(question, k=TOP_K)
    if _top_score(chunks) < MIN_RELEVANCE_SCORE:
        return {"answer": FALLBACK_ANSWER, "sources": [], "used_chunks": chunks}

    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {"role": "user", "content": prompts.build_user_message(question, chunks)},
    ]
    answer = fc.chat(messages)
    if _looks_like_bad_answer(answer):
        answer = _context_answer(chunks)

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
