"""
ui_streamlit.py  —  Streamlit arayüzü
Çalıştır:  streamlit run ui_streamlit.py
(Önce: python ingest.py ile veritabanı kurulmuş olmalı.)
"""
import streamlit as st

import db
import foundry_client as fc
from generation import answer_query


@st.cache_resource
def _warm_up() -> bool:
    """Modelleri sayfa açılırken bir kez yükler; ilk soru gecikmesiz cevaplanır."""
    fc.warm_up()
    return True

# ── Sayfa ayarları ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Local RAG Assistant",
    page_icon="🔍",
    layout="wide",
)

# ── Başlık ───────────────────────────────────────────────────────────────────
st.title("🔍 Local RAG Assistant")
st.caption("Foundry Local · SQLite · Offline · Source-grounded answers")

# ── DB durumu ────────────────────────────────────────────────────────────────
try:
    conn = db.get_connection()
    chunk_count = db.count_documents(conn)
    conn.close()
    if chunk_count == 0:
        st.warning(
            "⚠️  Veritabanı boş. Önce terminalde çalıştır: `python ingest.py`",
            icon="⚠️",
        )
    else:
        st.sidebar.success(f"✅ {chunk_count} chunk yüklü")
except Exception as e:
    st.error(f"DB bağlantı hatası: {e}")
    chunk_count = 0

# ── Model warm-up (sayfa açılışında bir kez) ─────────────────────────────────
if chunk_count > 0:
    try:
        with st.spinner("Modeller yükleniyor…"):
            _warm_up()
    except Exception as e:
        st.error(f"Modeller yüklenemedi: {e}")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Ayarlar")
    show_chunks = st.checkbox("Retrieved chunks göster (debug)", value=False)
    show_scores = st.checkbox("Similarity skorlarını göster", value=False)
    st.divider()
    st.markdown("**Nasıl çalışır?**")
    st.markdown(
        "1. Soruyu embed et\n"
        "2. rag.db'de cosine similarity ile en iyi 3 chunk'ı bul\n"
        "3. Chunk'ları prompt'a bağlam olarak ekle\n"
        "4. Foundry Local'den cevap al"
    )
    st.divider()
    if st.button("🗑️ Sohbet geçmişini temizle"):
        st.session_state.history = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Soru girişi ───────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    question = st.text_input(
        "Sorunuzu yazın:",
        placeholder="ör. RAG'in üç adımı nedir? / What is cosine similarity?",
        label_visibility="collapsed",
    )
with col_btn:
    ask_clicked = st.button("Sor →", use_container_width=True, type="primary")

# ── Cevap üretimi ─────────────────────────────────────────────────────────────
if ask_clicked and question.strip():
    if chunk_count == 0:
        st.error("Veritabanı boş. `python ingest.py` çalıştır.")
    else:
        with st.spinner("Düşünüyor…"):
            try:
                result = answer_query(question)
            except Exception as exc:
                result = {
                    "answer": f"Hata oluştu: {exc}",
                    "sources": [],
                    "used_chunks": [],
                }
        st.session_state.history.insert(0, (question, result))

# ── Sohbet geçmişi ────────────────────────────────────────────────────────────
for q, result in st.session_state.history:
    with st.container():
        st.markdown(f"**🧑 Soru:** {q}")

        # Cevap
        answer = result.get("answer", "Cevap alınamadı.")
        if "bilgi yok" in answer.lower() or "bulamadım" in answer.lower():
            st.info(answer, icon="ℹ️")
        else:
            st.markdown(answer)

        # Kaynaklar
        if result.get("sources"):
            src_list = " · ".join(f"`{s}`" for s in result["sources"])
            st.caption(f"📄 Kaynaklar: {src_list}")

        # Debug: retrieved chunks
        if show_chunks and result.get("used_chunks"):
            with st.expander("🔎 Retrieved chunks (debug)"):
                for i, c in enumerate(result["used_chunks"], 1):
                    score_str = (
                        f"  —  score: **{c['score']:.3f}**" if show_scores else ""
                    )
                    st.markdown(f"**Chunk {i}** · `{c['source']}`{score_str}")
                    st.text(c["text"][:400])
                    if i < len(result["used_chunks"]):
                        st.divider()

        st.divider()
