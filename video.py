DURACAO_PADRAO = 8

CAMERAS = [
    "Sony FX5",
    "Sony FX6",
    "Canon EOS C80",
    "ARRI Alexa Mini LF",
]

MOTORES_VIDEO = [
    "Veo",
    "Replicate",
    "Hugging Face",
]


def listar_motores():
    return MOTORES_VIDEO


def listar_cameras():
    return CAMERAS

# ============================================================
# MOTOR VEO / GEMINI
# ============================================================

def gerar_com_veo(
    prompt,
    duracao=8,
    proporcao="16:9",
    nome_arquivo="video_veo.mp4"
):
    """
    Geração de vídeo usando Google Gemini / Veo.
    """

    chave = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not chave:
        raise RuntimeError(
            "GEMINI_API_KEY não configurada."
        )

    try:
        from google import genai
    except ImportError:
        raise RuntimeError(
            "A biblioteca google-genai não está instalada."
        )

    client = genai.Client(
        api_key=chave
    )

    modelo = os.getenv(
        "VEO_MODEL",
        "veo-3.1-generate-preview"
    )

    print("🎬 Iniciando geração com Veo...")

    operacao = client.models.generate_videos(
        model=modelo,
        prompt=prompt
    )

    # Aguarda a geração terminar
    tentativas = 60

    for _ in range(tentativas):

        if getattr(
            operacao,
            "done",
            False
        ):
            break

        try:
            operacao = client.operations.get(
                operacao
            )
        except Exception:
            pass

        time.sleep(5)

    if not getattr(
        operacao,
        "done",
        False
    ):
        raise RuntimeError(
            "O Veo demorou demais para finalizar."
        )

    resultado = (
        getattr(
            operacao,
            "result",
            None
        )
        or
        getattr(
            operacao,
            "response",
            None
        )
    )

    if resultado is None:
        raise RuntimeError(
            "O Veo não retornou resultado."
        )

    videos = getattr(
        resultado,
        "generated_videos",
        None
    )

    if not videos:
        videos = getattr(
            resultado,
            "videos",
            None
        )

    if not videos:
        raise RuntimeError(
            "Nenhum vídeo foi retornado pelo Veo."
        )

    video = videos[0]

    arquivo = getattr(
        video,
        "video",
        None
    )

    if arquivo is None:
        arquivo = video

    caminho = (
        PASTA_VIDEOS /
        nome_arquivo
    )

    # Tenta baixar usando a SDK
    try:

        client.files.download(
            file=arquivo,
            path=str(caminho)
        )

    except Exception as erro:

        raise RuntimeError(
            f"Não foi possível salvar o vídeo: {erro}"
        )

    if not caminho.exists():

        raise RuntimeError(
            "O arquivo de vídeo não foi criado."
        )

    return str(caminho)
