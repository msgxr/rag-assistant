"""
ui_streamlit.py  —  Streamlit arayüzü  (Sahip: ŞEYMA)
Çalıştır:  streamlit run ui_streamlit.py
(Önce: python ingest.py ile veritabanı kurulmuş olmalı.)
"""
import streamlit as st

from generation import answer_query

st.set_page_config(page_title="Yerel RAG Asistanı", page_icon="📄")
st.title("📄 Yerel RAG Asistanı")
st.caption("Foundry Local + RAG — internetsiz, kaynağa dayalı cevap")

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_input("Sorunuzu yazın:",
                         placeholder="ör. Bu döküman ne anlatıyor?")
show_chunks = st.checkbox("Getirilen parçaları göster (debug)", value=False)

if st.button("Sor") and question.strip():
    with st.spinner("Düşünüyor... (ilk soruda modeller yükleniyor olabilir)"):
        result = answer_query(question)
    st.session_state.history.insert(0, (question, result))

for q, result in st.session_state.history:
    st.markdown(f"**Soru:** {q}")
    st.markdown(result["answer"])
    if result["sources"]:
        st.caption("Kaynaklar: " + ", ".join(result["sources"]))
    if show_chunks and result["used_chunks"]:
        with st.expander("Getirilen parçalar"):
            for c in result["used_chunks"]:
                st.markdown(f"`{c['source']}`  —  skor: {c['score']:.3f}")
                st.text(c["text"])
    st.divider()
