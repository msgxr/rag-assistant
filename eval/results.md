# RAG Evaluation Sonuçları

- **Tarih:** 2026-07-27 00:28
- **Geçti:** 22/26  ·  **Kaldı:** 4/26  ·  **Ortalama süre:** 44.53s/soru

| # | Tip | Sonuç | Süre (s) | Soru | Değerlendirme | Kaynaklar |
|---|-----|-------|----------|------|---------------|-----------|
| 01 | answerable | PASS | 128.28 | Foundry Local Intel Mac'lerde çalışır mı? | correct | foundry_local.md |
| 02 | answerable | FAIL | 27.86 | Foundry Local hangi donanım hızlandırma yöntemlerini kullanır? | expected 'gpu' not found in answer | foundry_local.md, architecture.md |
| 03 | answerable | PASS | 30.81 | Foundry Local'de model nasıl indirilir? | correct | foundry_local.md, architecture.md |
| 04 | answerable | PASS | 32.63 | qwen2.5-0.5b modeli ne zaman tercih edilmeli? | correct | foundry_local.md, architecture.md |
| 05 | answerable | PASS | 54.68 | RAG'in üç adımı nedir? | correct | rag_nedir.md, rag_pipeline.md |
| 06 | answerable | PASS | 32.58 | Halüsinasyon nedir? | correct | rag_nedir.md, prompt_engineering.md |
| 07 | answerable | PASS | 62.18 | RAG ne zaman kullanılır? | correct | rag_nedir.md, prompt_engineering.md |
| 08 | answerable | PASS | 33.48 | Cosine similarity nedir? | correct | embeddings.md, sqlite.md |
| 09 | answerable | PASS | 28.24 | Top-K retrieval'da K değeri bu projede kaçtır? | correct | embeddings.md, prompt_engineering.md |
| 10 | answerable | PASS | 69.53 | Embedding modeli ile chat modeli arasındaki fark nedir? | correct | embeddings.md, architecture.md, rag_pipeline.md |
| 11 | answerable | PASS | 65.62 | SQLite veriyi nerede saklar? | correct | sqlite.md |
| 12 | answerable | PASS | 35.83 | documents tablosundaki dört sütunun adları nelerdir? | correct | sqlite.md |
| 13 | answerable | FAIL | 51.88 | rag.db nasıl yeniden oluşturulur? | expected 'ingest' not found in answer | rag_nedir.md, rag_pipeline.md |
| 14 | answerable | PASS | 38.06 | RAG promptlarında system prompt ne işe yarar? | correct | prompt_engineering.md |
| 15 | answerable | FAIL | 11.69 | Neden cevaplarda kaynak dosya adı gösterilir? | gave fallback when answer exists in docs | - |
| 16 | answerable | PASS | 68.46 | ingest.py ne yapar? | correct | rag_pipeline.md, prompt_engineering.md |
| 17 | answerable | PASS | 36.98 | Varsayılan chunk boyutu kaç karakterdir? | correct | rag_pipeline.md, embeddings.md |
| 18 | answerable | FAIL | 83.34 | Minimum benzerlik skoru nedir? | expected '0.45' not found in answer | rag_pipeline.md, embeddings.md |
| 19 | unanswerable | PASS | 8.35 | Bu projenin bütçesi ne kadar? | correct fallback | - |
| 20 | unanswerable | PASS | 4.00 | İstanbul'da bugün hava nasıl? | correct fallback | - |
| 21 | unanswerable | PASS | 5.17 | 2026 dünya kupasını kim kazandı? | correct fallback | - |
| 22 | unanswerable | PASS | 81.36 | Foundry Local'in hisse fiyatı nedir? | correct fallback | - |
| 23 | edge | PASS | 0.00 | (boş) | handled gracefully | - |
| 24 | edge | PASS | 61.97 | RAG | handled gracefully | prompt_engineering.md, architecture.md |
| 25 | edge | PASS | 40.02 | Bana her şeyi anlat | handled gracefully | prompt_engineering.md |
| 26 | edge | PASS | 64.79 | Merhaba, ben bu projeyi yeni kurdum ve dökümanları okumaya vaktim olmadı, bana lütfen bu sistemin ne işe yaradığını, hangi teknolojileri kullandığını, verilerin nerede saklandığını, embedding denen şeyin ne olduğunu ve bir sorunun cevabının adım adım nasıl üretildiğini tek seferde, olabildiğince ayrıntılı şekilde anlatır mısın? | handled gracefully | rag_nedir.md, prompt_engineering.md, rag_pipeline.md |
