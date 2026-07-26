# Final Presentation Outline — Local RAG Assistant

5 dakikalık demo günü sunumunun iskeleti. Her bölümün yanında hedef süre var;
sunumdan önce en az bir kez hedef makinede prova yapın.

---

## 1. Problem Statement (~1 dk)

- Genel LLM'ler kendi dökümanlarınızı bilmez; bilmediğinde de **uydurabilir**
  (halüsinasyon).
- Kurum içi/kişisel dökümanlar için soruların **cevabı kaynaklı** olmalı ve veri
  **cihazdan dışarı çıkmamalı** (gizlilik, çevrimdışı çalışma).
- Hedef: internet bağlantısı olmadan, kendi döküman koleksiyonu üzerinden soru
  cevaplayan, kaynak gösteren ve bilmediğinde "bilmiyorum" diyen bir asistan.

## 2. Key Features & Components (~1 dk)

- **RAG deseni:** getir (retrieve) → zenginleştir (augment) → üret (generate).
- **Katmanlar (tek makinede):**
  - Arayüz: `main.py` (CLI) veya `ui_streamlit.py` (web)
  - Uygulama/pipeline: `generation.answer_query()` + `retrieval.get_top_chunks()`
  - Veri: SQLite `rag.db` (chunk metni + JSON embedding, `db.py`)
  - AI: Foundry Local — `qwen2.5-1.5b` (chat) + `qwen3-embedding-0.6b` (embedding),
    tamamen cihaz üzerinde
- **Sorumlu cevaplar:** benzerlik skoru 0.45 altındaysa veya model bağlamda cevap
  bulamadıysa tek biçimli fallback: *"Bu konuda elimdeki dökümanlarda bilgi yok."*
- **Kaynak gösterimi:** her cevabın altında `[kaynak: dosya.md]`.

## 3. Live Demo (~2 dk)

Demo öncesi: `python ingest.py` çalıştırılmış, `rag.db` dolu olmalı.

1. `data/` klasörünü göster — bilgi tabanındaki 7 dökümanı kısaca tanıt.
2. **Cevaplanabilir soru** sor (ör. "RAG'in üç adımı nedir?") — cevabı ve
   `[kaynak: ...]` satırını göster.
3. **Cevaplanamaz soru** sor (ör. "İstanbul'da bugün hava nasıl?") — asistanın
   uydurmak yerine fallback mesajını verdiğini göster.
4. Streamlit'te **"Retrieved chunks (debug)"** panelini aç — modelin cevabı hangi
   parçalardan ürettiğini göster (retrieval'ın kanıtı).
5. (İsteğe bağlı) `python eval/run_eval.py` çıktısı ve `eval/results.md` ile test
   sonuçlarını göster.

## 4. Lessons Learned (~1 dk)

Kendi deneyiminize göre 1-2 tanesini seçip kısaca anlatın; örnekler:

- Döküman **parçalama stratejisi** (chunk boyutu/örtüşme) retrieval kalitesini
  doğrudan belirliyor — yanlış bölünen paragraf yanlış cevap demek.
- **Eşik ayarı** bir denge işi: 0.45 çok düşükse alakasız bağlam geliyor, çok
  yüksekse cevaplanabilir sorular reddediliyor.
- Küçük modellerde **prompt disiplini** kritik: talimatlar net olmazsa model
  talimat metnini tekrarlayabiliyor.
- **Eval seti** ile ilerlemek tahminle ilerlemekten çok daha hızlı: her
  değişiklikten sonra `run_eval.py` koşup PASS/FAIL farkına bakmak yetiyor.

---

**Kapanış cümlesi önerisi:** "Tamamen çevrimdışı, kaynak gösteren ve bilmediğini
söyleyebilen bir soru-cevap asistanını bir ayda, tamamen yerel araçlarla kurduk."
