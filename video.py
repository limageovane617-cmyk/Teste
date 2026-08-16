import os
import time
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_VIDEOS = Path("videos")
PASTA_VIDEOS.mkdir(exist_ok=True)

DURACAO_PADRAO = 8

PROPORCOES = [
    "16:9",
    "9:16",
    "1:1",
]

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


# ============================================================
# FUNÇÕES BÁSICAS
# ============================================================

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
    Gera vídeo usando Google Gemini / Veo.
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

    # --------------------------------------------------------
    # INICIA GERAÇÃO
    # --------------------------------------------------------

    operacao = client.models.generate_videos(
        model=modelo,
        prompt=prompt
    )

    # --------------------------------------------------------
    # AGUARDA RESULTADO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # VERIFICA SE TERMINOU
    # --------------------------------------------------------

    if not getattr(
        operacao,
        "done",
        False
    ):

        raise RuntimeError(
            "O Veo demorou demais para finalizar."
        )

    # --------------------------------------------------------
    # PEGA RESULTADO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PEGA VÍDEOS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SALVA ARQUIVO
    # --------------------------------------------------------

    caminho = (
        PASTA_VIDEOS /
        nome_arquivo
    )

    try:

        client.files.download(
            file=arquivo,
            path=str(caminho)
        )

    except Exception as erro:

        raise RuntimeError(
            f"Não foi possível salvar o vídeo: {erro}"
        )

    # --------------------------------------------------------
    # CONFIRMA ARQUIVO
    # --------------------------------------------------------

    if not caminho.exists():

        raise RuntimeError(
            "O arquivo de vídeo não foi criado."
        )

    return str(caminho)


# ============================================================
# PROMPT DE VÍDEO
# ============================================================

def montar_prompt_video(
    descricao,
    camera="Sony FX6",
    proporcao="16:9",
    duracao=8
):

    return f"""
Crie um vídeo cinematográfico de aproximadamente
{duracao} segundos.

DESCRIÇÃO:
{descricao}

CÂMERA:
{camera}

PROPORÇÃO:
{proporcao}

CONTINUIDADE DO PERSONAGEM:

- manter exatamente o mesmo personagem;
- manter o mesmo rosto;
- manter o mesmo cabelo;
- manter o mesmo corpo;
- manter a mesma roupa;
- manter os mesmos acessórios;
- manter a mesma identidade visual;
- se a câmera sair do personagem e retornar,
  mostrar exatamente o mesmo personagem;
- não trocar a roupa;
- não trocar o rosto;
- não criar uma segunda versão do personagem;
- manter iluminação consistente;
- manter cenário consistente;
- evitar deformações;
- evitar personagens duplicados;
- movimentos naturais;
- câmera cinematográfica suave.

ESTILO:

cinematográfico,
realista,
alta qualidade,
movimentos naturais.
""".strip()


# ============================================================
# GERADOR DE VÍDEO
# ============================================================

def gerar_video(
    descricao,
    camera="Sony FX6",
    proporcao="16:9",
    duracao=8,
    nome_arquivo="video.mp4"
):

    prompt = montar_prompt_video(
        descricao=descricao,
        camera=camera,
        proporcao=proporcao,
        duracao=duracao
    )

    caminho = gerar_com_veo(
        prompt=prompt,
        duracao=duracao,
        proporcao=proporcao,
        nome_arquivo=nome_arquivo
    )

    return {
        "sucesso": True,
        "motor": "Veo",
        "caminho": caminho,
        "prompt": prompt
    }


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    print(
        "🎬 Alex IA Ultra"
    )

    print(
        "Motores:",
        listar_motores()
    )

    print(
        "Câmeras:",
        listar_cameras()
    )

    print(
        "Duração:",
        DURACAO_PADRAO,
        "segundos"
    )

    print(
        "✅ video.py carregado corretamente."
    )
# ============================================================
# TESTE DE AUTENTICAÇÃO GEMINI
# ============================================================

def testar_gemini():

    chave = os.getenv("GEMINI_API_KEY")

    if not chave:
        return {
            "ok": False,
            "erro": "GEMINI_API_KEY não encontrada."
        }

    try:
        from google import genai

        client = genai.Client(
            api_key=chave
        )

        # Faz uma chamada simples ao Gemini
        resposta = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents="Responda apenas: OK"
        )

        texto = getattr(
            resposta,
            "text",
            ""
        )

        return {
            "ok": True,
            "resposta": texto
        }

    except Exception as erro:

        return {
            "ok": False,
            "erro": str(erro)
        }
