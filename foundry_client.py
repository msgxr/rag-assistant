"""
foundry_client.py  —  Foundry Local ÇEKİRDEĞİ  (Sahip: SİNA)

Projedeki TEK Foundry SDK temas noktası. db / retrieval / generation
hep buradan import eder; başka hiçbir dosya SDK'ya dokunmaz.
Böylece SDK sürümü değişirse sadece bu dosyayı güncellersin.

Kurulum (requirements.txt platforma göre otomatik seçer):
    Windows : pip install foundry-local-sdk-winml
    macOS   : pip install foundry-local-sdk
Her iki pakette de import adı aynı:  foundry_local_sdk

NOT: Aşağıdaki alias'ları kendi makinende `foundry model list` ile DOĞRULA.
"""
from __future__ import annotations
import threading

from foundry_local_sdk import Configuration, FoundryLocalManager

# --- Model alias'ları (foundry model list ile doğrula) ---------------------
CHAT_MODEL_ALIAS = "qwen2.5-1.5b"             # hız/kalite dengesi. Daha hızlı: "qwen2.5-0.5b", daha iyi: "phi-3.5-mini"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"   # makinende embedding modelinin alias'ını doğrula

# --- Üretim ayarları --------------------------------------------------------
TEMPERATURE = 0.2
MAX_TOKENS  = 256    # 1-3 cümlelik cevap için yeterli; kısa tutmak hem hız hem odak sağlar

# --- Tembel (lazy) tekil başlatma; modeller programda 1 kez yüklenir --------
_lock = threading.Lock()
_ready = False
_chat_model = None
_chat_client = None
_embed_model = None
_embed_client = None


def _safe_download(model, model_name: str = "") -> None:
    """Model cache'te yoksa indir; varsa sessizce geç. Sürüm farklarına dayanıklı."""
    dl = getattr(model, "download", None)
    if not callable(dl):
        return
    try:
        dl()
    except TypeError:
        try:
            dl(lambda *a, **k: None)
        except Exception as exc:
            print(f"[!] {model_name} indirilemedi (cache'te varsa sorun değil): {exc}")
    except Exception as exc:
        print(f"[!] {model_name} indirilemedi (cache'te varsa sorun değil): {exc}")


def _ensure_ready() -> None:
    global _ready, _chat_model, _chat_client, _embed_model, _embed_client
    if _ready:
        return
    with _lock:
        if _ready:
            return
        config = Configuration(app_name="rag-assistant")
        FoundryLocalManager.initialize(config)
        manager = FoundryLocalManager.instance
        catalog = manager.catalog

        # Chat modeli
        _chat_model = catalog.get_model(CHAT_MODEL_ALIAS)
        _safe_download(_chat_model, CHAT_MODEL_ALIAS)
        try:
            _chat_model.load()
        except Exception as exc:
            raise RuntimeError(
                f"Chat modeli '{CHAT_MODEL_ALIAS}' yüklenemedi: {exc}"
            ) from exc
        _chat_client = _chat_model.get_chat_client()
        try:
            _chat_client.settings.temperature = TEMPERATURE
            _chat_client.settings.max_tokens = MAX_TOKENS
        except Exception as exc:
            print(f"[!] Chat model ayarları uygulanamadı: {exc}")

        # Embedding modeli
        _embed_model = catalog.get_model(EMBEDDING_MODEL_ALIAS)
        _safe_download(_embed_model, EMBEDDING_MODEL_ALIAS)
        try:
            _embed_model.load()
        except Exception as exc:
            raise RuntimeError(
                f"Embedding modeli '{EMBEDDING_MODEL_ALIAS}' yüklenemedi: {exc}"
            ) from exc
        _embed_client = _embed_model.get_embedding_client()

        _ready = True


def _extract_embedding(resp) -> list[float]:
    """
    Embedding response şekli SDK sürümüne göre değişebilir.
    Yaygın şekilleri sırayla dener; tanıyamazsa anlaşılır hata verir.
    """
    data = getattr(resp, "data", None)
    if data:
        first = data[0]
        emb = getattr(first, "embedding", None)
        if emb is not None:
            return list(emb)
        if isinstance(first, dict) and "embedding" in first:
            return list(first["embedding"])
    emb = getattr(resp, "embedding", None)
    if emb is not None:
        return list(emb)
    if isinstance(resp, (list, tuple)):
        return list(resp)
    raise RuntimeError(
        "Embedding response şekli tanınamadı; _extract_embedding'i SDK sürümüne "
        f"göre güncelle. Gelen tip: {type(resp)!r}"
    )


# ===================== Dışarıya açık API (sözleşme) =========================

def warm_up() -> None:
    """Modelleri program başında yükler; ilk soruda bekleme yaşanmaz."""
    _ensure_ready()


def get_embedding(text: str) -> list[float]:
    """Tek metni embedding vektörüne çevirir. -> list[float]"""
    _ensure_ready()
    return _extract_embedding(_embed_client.generate_embedding(text))


def chat(messages: list[dict]) -> str:
    """
    OpenAI-uyumlu mesaj listesi alır, modelin metin cevabını döndürür.
    messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
    -> str
    """
    _ensure_ready()
    resp = _chat_client.complete_chat(messages)
    return resp.choices[0].message.content


def shutdown() -> None:
    """Program sonunda modelleri bellekten boşalt (opsiyonel)."""
    for m in (_chat_model, _embed_model):
        try:
            if m is not None:
                m.unload()
        except Exception:
            pass
