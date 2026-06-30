"""
prompts.py  —  System prompt + bağlam şablonu  (Sahip: ŞEYMA)
"""
from __future__ import annotations

SYSTEM_PROMPT = """Sen yerel dökümanlara dayalı cevap veren bir asistansın.

Kurallar:
1. SADECE sana verilen "BAĞLAM" bölümündeki bilgiyi kullan.
2. Bağlamda cevap yoksa aynen şunu yaz: "Bu konuda elimdeki dökümanlarda bilgi yok."
   Tahmin etme, dışarıdan bilgi ekleme, uydurma.
3. Cevabı kısa ve net tut.
4. Kullandığın bilginin kaynağını belirt (ör. [kaynak: dosya.md]).
5. Her zaman Türkçe cevap ver."""


def build_user_message(question: str, chunks: list[dict]) -> str:
    """Getirilen parçaları BAĞLAM olarak biçimleyip soruyla birleştirir."""
    if chunks:
        blocks = [f"[kaynak: {c['source']}]\n{c['text']}" for c in chunks]
        context = "\n\n---\n\n".join(blocks)
    else:
        context = "(ilgili bağlam bulunamadı)"
    return f"BAĞLAM:\n{context}\n\nSORU: {question}\n\nCevap:"
