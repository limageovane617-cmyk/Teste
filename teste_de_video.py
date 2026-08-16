import streamlit as st
import video

st.set_page_config(
    page_title="Alex IA - Teste de Vídeo",
    page_icon="🎬"
)

st.title("🎬 Alex IA — Teste do Veo")

st.success("Sistema de vídeo carregado!")

descricao = st.text_area(
    "Descrição do vídeo",
    value="Um robô humanoide caminhando por uma cidade futurista à noite, com luzes cinematográficas."
)

camera = st.selectbox(
    "Câmera",
    video.listar_cameras()
)

proporcao = st.selectbox(
    "Proporção",
    video.PROPORCOES
)

if st.button("🎬 Gerar vídeo com Veo"):

    with st.spinner("Gerando vídeo com Veo..."):

        try:

            resultado = video.gerar_video(
                descricao=descricao,
                camera=camera,
                proporcao=proporcao,
                duracao=8,
                nome_arquivo="teste_veo.mp4"
            )

            if resultado["sucesso"]:

                st.success(
                    "✅ Vídeo gerado com sucesso!"
                )

                st.video(
                    resultado["caminho"]
                )

                st.write(
                    "Motor usado:",
                    resultado["motor"]
                )

            else:

                st.error(
                    "❌ Não foi possível gerar o vídeo."
                )

        except Exception as erro:

            st.error(
                "❌ Erro ao gerar vídeo:"
            )

            st.code(
                str(erro)
            )
