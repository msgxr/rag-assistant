# Yerel RAG Asistanı (Foundry Local + RAG)

İnternetsiz çalışan döküman Q&A asistanı. Kullanıcının sorusuna, yerel döküman
havuzundan ilgili parçaları bulup (RAG) on-device LLM ile kaynağa dayalı cevap üretir.
Tüm çalışma çevrimdışı; sıfır network çağrısı (modeller ilk kez indirildikten sonra).

**Ekip:** Muhammed Sina (HP/Windows) + Şeyma (Mac/Apple Silicon)

---

## 0. Ön koşul (önce bunu doğrula)

Foundry Local **yalnızca Apple Silicon** Mac'i destekler (M1/M2/M3/M4). Şeyma'nın
Mac'i Intel ise bu proje o makinede çalışmaz — Linux/Windows alternatifi gerekir.

Gereken: Python 3.10+ ve ilk model indirmesi için (bir kerelik) internet.

---

## 1. Kurulum

```bash
# 1) sanal ortam
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS:
source .venv/bin/activate

# 2) bağımlılıklar (requirements.txt platforma göre doğru Foundry paketini seçer)
pip install -r requirements.txt
```

### Model alias'larını doğrula  (ÖNEMLİ)
Makinende hangi modellerin mevcut olduğunu gör:
```bash
foundry model list
```
Sonra `foundry_client.py` içindeki iki sabiti kendi makinendekiyle eşle:
```python
CHAT_MODEL_ALIAS      = "qwen2.5-0.5b"          # hızlı; kalite için "phi-3.5-mini"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"  # listedeki embedding modelinin alias'ı
```

---

## 2. Çalıştırma

```bash
# 1) veritabanını kur (data/ içindeki dökümanları parçalar + embed eder)
python ingest.py

# 2a) CLI ile sor-cevap
python main.py

# 2b) veya web arayüzü
streamlit run ui_streamlit.py
```

İlk soruda modeller belleğe yüklenir (biraz sürebilir); sonrası hızlıdır.

### Kendi dökümanlarını ekle
`data/` klasörüne `.txt` veya `.md` dosyalarını at, `python ingest.py` komutunu
tekrar çalıştır. (Ingestion her seferinde DB'yi temizleyip yeniden kurar.)

---

## 3. Test / Değerlendirme

```bash
python eval/run_eval.py
```
`eval/questions.yaml` içindeki soruları koşar; cevaplanabilir sorularda doğru bilgi,
cevaplanamaz sorularda "bilmiyorum" davranışını kontrol eder. **İki makinede de**
koşturup karşılaştırın — Mac ve Windows farklı model varyantı indirdiği için cevaplar
birebir aynı çıkmayabilir.

---

## 4. Mimari ve veri akışı

```
[Kullanıcı/UI] -> [generation.answer_query] -> [retrieval.get_top_chunks] -> [SQLite]
                          |                                                      
                          v                                                      
                  [foundry_client.chat]  <- (Foundry Local on-device LLM)        
```

1. Soru embed edilir, SQLite'taki vektörlerle cosine similarity ile karşılaştırılır
   -> en iyi k parça (**retrieve**).
2. Parçalar system prompt'a bağlam olarak eklenir (**augment**).
3. Foundry chat modeli cevabı üretir; bağlamda yoksa "bilmiyorum" der (**generate**).

---

## 5. Dosya sahipliği (kim ne yazar)

| Dosya | Sahip | İş |
|-------|-------|----|
| `foundry_client.py` | **Sina** | Foundry init + `get_embedding()` + `chat()` (tek SDK noktası) |
| `db.py` | **Sina** | SQLite şema + I/O |
| `ingest.py` | **Sina** | böl -> embed -> SQLite |
| `retrieval.py` | **Sina** | `get_top_chunks()` (cosine similarity) |
| `prompts.py` | **Şeyma** | system prompt + bağlam şablonu |
| `generation.py` | **Şeyma** | `answer_query()` |
| `ui_streamlit.py` | **Şeyma** | Streamlit arayüzü |
| `main.py` | Ortak | CLI giriş |
| `data/`, `eval/`, `README` | Ortak | dökümanlar, test, dok |

**Arayüz sözleşmesi (değişmez):**
```python
foundry_client.get_embedding(text: str) -> list[float]
foundry_client.chat(messages: list[dict]) -> str
retrieval.get_top_chunks(query: str, k: int = 3) -> list[dict]   # {text, source, score}
generation.answer_query(question: str) -> dict                   # {answer, sources, used_chunks}
```
> Şeyma, Sina'nın parçası hazır olmadan `get_top_chunks`'ı mock'layıp UI'ı geliştirebilir.

---

## 6. Git akışı

- `main` her zaman çalışır. Direkt push yok.
- Branch: `feat/retrieval`, `feat/ui`, `feat/generation` ...
- Küçük + sık commit, PR aç, diğer kişi bakar, Sina merge eder.

---

## 7. Kabul kriterleri (Definition of Done)

- [ ] Cevap dökümanlardaysa -> doğru, kaynak gösteren cevap
- [ ] Bilgi yoksa -> "Bu konuda elimdeki dökümanlarda bilgi yok" (uydurmaz)
- [ ] Boş/çok genel sorgu çökmeden işlenir
- [ ] Tek komutla kurulup çalışır (`pip install -r requirements.txt`)
- [ ] **Hem HP hem Mac'te** çalışır
- [ ] `eval/run_eval.py` geçer; README + demo hazır
