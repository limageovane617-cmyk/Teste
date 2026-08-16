import streamlit as st
import video

st.set_page_config(
    page_title="Alex IA - Teste de Vídeo",
    page_icon="🎬"
)

st.title("🎬 Alex IA — Teste do Motor de Vídeo")

st.success("Streamlit funcionando!")

st.write("### Motores encontrados:")

for motor in video.listar_motores():
    st.write("✅", motor)

st.write("### Câmeras disponíveis:")

for camera in video.listar_cameras():
    st.write("📷", camera)
