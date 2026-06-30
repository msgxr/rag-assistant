"""
main.py  —  CLI giriş noktası

Kullanım:
    python ingest.py     # önce bir kez: veritabanını kur
    python main.py       # soru-cevap döngüsü (CLI)
veya UI için:
    streamlit run ui_streamlit.py
"""
from __future__ import annotations

import db
import foundry_client as fc
from generation import answer_query


def main() -> None:
    conn = db.get_connection()
    db.init_db(conn)
    n = db.count_documents(conn)
    conn.close()
    if n == 0:
        print("[!] Veritabanı boş. Önce çalıştır:  python ingest.py")
        return

    print("=== Yerel RAG Asistanı ===  (çıkmak için: exit)\n")
    try:
        while True:
            q = input("Soru> ").strip()
            if q.lower() in {"exit", "quit", "q", "çık", "cik"}:
                break
            if not q:
                continue
            r = answer_query(q)
            print("\n" + r["answer"])
            if r["sources"]:
                print(f"\n(kaynaklar: {', '.join(r['sources'])})")
            print()
    finally:
        fc.shutdown()


if __name__ == "__main__":
    main()
