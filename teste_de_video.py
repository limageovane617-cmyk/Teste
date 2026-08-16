import streamlit as st
import video

st.set_page_config(
    page_title="Alex IA — Imagem para Vídeo",
    page_icon="🎬"
)

st.title("🎬 Alex IA — Imagem → Vídeo")

st.write(
    "Envie uma imagem e descreva o movimento "
    "que você quer transformar em vídeo."
)

# ============================================================
# IMAGEM
# ============================================================

imagem = st.file_uploader(
    "🖼️ Escolha uma imagem",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp"
    ]
)

if imagem:

    st.image(
        imagem,
        caption="Imagem de referência",
        use_container_width=True
    )

# ============================================================
# MOVIMENTO
# ============================================================

movimento = st.text_area(
    "🎬 Descreva o movimento",
    placeholder=(
        "Exemplo: o personagem começa a caminhar "
        "lentamente em direção à câmera enquanto "
        "o vento movimenta sua roupa."
    ),
    height=120
)

# ============================================================
# CÂMERA
# ============================================================

camera = st.selectbox(
    "📷 Câmera",
    video.listar_cameras()
)

# ============================================================
# PROPORÇÃO
# ============================================================

proporcao = st.selectbox(
    "📐 Proporção",
    video.listar_proporcoes()
)

# ============================================================
# BOTÃO
# ============================================================

if st.button(
    "🎬 Gerar vídeo",
    type="primary"
):

    if imagem is None:

        st.warning(
            "🖼️ Primeiro envie uma imagem."
        )

    elif not movimento.strip():

        st.warning(
            "✍️ Descreva o movimento do vídeo."
        )

    else:

        with st.spinner(
            "🎬 Gerando vídeo a partir da imagem..."
        ):

            try:

                resultado = video.gerar_video(
                    imagem=imagem,
                    movimento=movimento,
                    camera=camera,
                    proporcao=proporcao,
                    duracao=5,
                    nome_arquivo="video_i2v.mp4"
                )

                st.success(
                    "✅ Vídeo gerado!"
                )

                st.video(
                    resultado["caminho"]
                )

                st.write(
                    "🎥 Motor:",
                    resultado["motor"]
                )

            except Exception as erro:

                st.error(
                    "❌ Não foi possível gerar o vídeo."
                )

                st.code(
                    str(erro)
                )
