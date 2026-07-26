# RAG Evaluation Sonuçları

- **Tarih:** 2026-07-26 23:38
- **Geçti:** 23/26  ·  **Kaldı:** 3/26  ·  **Ortalama süre:** 20.97s/soru

| # | Tip | Sonuç | Süre (s) | Soru | Değerlendirme | Kaynaklar |
|---|-----|-------|----------|------|---------------|-----------|
| 01 | answerable | PASS | 36.43 | Foundry Local Intel Mac'lerde çalışır mı? | correct | foundry_local.md |
| 02 | answerable | FAIL | 13.64 | Foundry Local hangi donanım hızlandırma yöntemlerini kullanır? | expected 'gpu' not found in answer | foundry_local.md, architecture.md |
| 03 | answerable | PASS | 13.81 | Foundry Local'de model nasıl indirilir? | correct | foundry_local.md, architecture.md |
| 04 | answerable | PASS | 18.04 | qwen2.5-0.5b modeli ne zaman tercih edilmeli? | correct | foundry_local.md, architecture.md |
| 05 | answerable | PASS | 12.93 | RAG'in üç adımı nedir? | correct | rag_nedir.md |
| 06 | answerable | PASS | 17.65 | Halüsinasyon nedir? | correct | rag_nedir.md, prompt_engineering.md |
| 07 | answerable | PASS | 23.83 | RAG ne zaman kullanılır? | correct | rag_nedir.md |
| 08 | answerable | PASS | 28.28 | Cosine similarity nedir? | correct | embeddings.md |
| 09 | answerable | PASS | 14.02 | Top-K retrieval'da K değeri bu projede kaçtır? | correct | embeddings.md, rag_pipeline.md |
| 10 | answerable | PASS | 25.73 | Embedding modeli ile chat modeli arasındaki fark nedir? | correct | embeddings.md |
| 11 | answerable | PASS | 42.30 | SQLite veriyi nerede saklar? | correct | sqlite.md |
| 12 | answerable | PASS | 18.94 | documents tablosundaki dört sütunun adları nelerdir? | correct | sqlite.md |
| 13 | answerable | PASS | 20.16 | rag.db nasıl yeniden oluşturulur? | correct | architecture.md, sqlite.md, rag_nedir.md |
| 14 | answerable | PASS | 20.32 | RAG promptlarında system prompt ne işe yarar? | correct | prompt_engineering.md |
| 15 | answerable | PASS | 47.46 | Neden cevaplarda kaynak dosya adı gösterilir? | correct | prompt_engineering.md, rag_nedir.md |
| 16 | answerable | FAIL | 22.21 | ingest.py ne yapar? | gave fallback when answer exists in docs | - |
| 17 | answerable | FAIL | 18.03 | Varsayılan chunk boyutu kaç karakterdir? | gave fallback when answer exists in docs | - |
| 18 | answerable | PASS | 16.96 | Minimum benzerlik skoru nedir? | correct | rag_pipeline.md, embeddings.md |
| 19 | unanswerable | PASS | 2.02 | Bu projenin bütçesi ne kadar? | correct fallback | - |
| 20 | unanswerable | PASS | 1.80 | İstanbul'da bugün hava nasıl? | correct fallback | - |
| 21 | unanswerable | PASS | 2.95 | 2026 dünya kupasını kim kazandı? | correct fallback | - |
| 22 | unanswerable | PASS | 15.07 | Foundry Local'in hisse fiyatı nedir? | correct fallback | - |
| 23 | edge | PASS | 0.00 | (boş) | handled gracefully | - |
| 24 | edge | PASS | 21.89 | RAG | handled gracefully | rag_pipeline.md, architecture.md, embeddings.md |
| 25 | edge | PASS | 12.33 | Bana her şeyi anlat | handled gracefully | prompt_engineering.md, rag_pipeline.md |
| 26 | edge | PASS | 78.30 | Merhaba, ben bu projeyi yeni kurdum ve dökümanları okumaya vaktim olmadı, bana lütfen bu sistemin ne işe yaradığını, hangi teknolojileri kullandığını, verilerin nerede saklandığını, embedding denen şeyin ne olduğunu ve bir sorunun cevabının adım adım nasıl üretildiğini tek seferde, olabildiğince ayrıntılı şekilde anlatır mısın? | handled gracefully | embeddings.md, rag_nedir.md |
