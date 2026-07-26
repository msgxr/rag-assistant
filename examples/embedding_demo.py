"""
embedding_demo.py  —  Embedding ve benzerlik demosu (Hafta 2)

Küçük bir cümle listesini embedding vektörlerine çevirir, verilen sorguyu da
embed edip cosine similarity ile en benzer cümleyi bulur. RAG'in "retrieve"
adımının en yalın hali — veritabanı yok, her şey bellekte.

Çalıştır (proje kökünden):
    python examples/embedding_demo.py
    python examples/embedding_demo.py "Veriler nerede saklanır?"
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

# Windows terminali bazen CP1254 kullanır; Türkçe karakterler için UTF-8'e geç
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# examples/ içinden çalıştırılınca proje kökünü import yoluna ekle
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import foundry_client as fc  # noqa: E402

SENTENCES = [
    "RAG, cevap üretmeden önce ilgili dökümanları getirir.",
    "SQLite veriyi sunucu gerektirmeden tek bir dosyada saklar.",
    "Embedding, metnin anlamını sayısal bir vektörle temsil eder.",
    "Foundry Local modelleri tamamen cihaz üzerinde, çevrimdışı çalıştırır.",
    "Prompt mühendisliği modelin davranışını yönlendirir.",
]


def cosine(a: list[float], b: list[float]) -> float:
    """İki vektör arasındaki cosine similarity (retrieval.py ile aynı mantık)."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def main() -> None:
    query = " ".join(sys.argv[1:]) or "Vektör veritabanı ne işe yarar?"

    print(f"[->] Embedding modeli: {fc.EMBEDDING_MODEL_ALIAS}")
    print(f"[->] {len(SENTENCES)} cümle embed ediliyor...\n")
    embeddings = [fc.get_embedding(s) for s in SENTENCES]
    query_emb = fc.get_embedding(query)

    # Her cümle için benzerlik skorunu hesapla, en yüksekten düşüğe sırala
    scored = sorted(
        ((cosine(query_emb, emb), sent) for emb, sent in zip(embeddings, SENTENCES)),
        reverse=True,
    )

    print(f"SORGU: {query}\n")
    for rank, (score, sentence) in enumerate(scored, 1):
        marker = "  <-- en benzer" if rank == 1 else ""
        print(f"  {rank}. [{score:.3f}] {sentence}{marker}")

    fc.shutdown()


if __name__ == "__main__":
    main()
