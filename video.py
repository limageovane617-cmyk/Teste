"""
Alex IA Ultra
Gerador de vídeo a partir de imagem + descrição de movimento.

Fluxo:
    imagem -> prompt de movimento -> vídeo

O arquivo foi feito para funcionar no Streamlit Cloud
sem tentar carregar modelos gigantes localmente.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_VIDEOS = Path("videos")
PASTA_VIDEOS.mkdir(parents=True, exist_ok=True)

DURACAO_PADRAO = 5

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
    "Hugging Face",
]


# ============================================================
# LISTAS
# ============================================================

def listar_motores():
    return MOTORES_VIDEO


def listar_cameras():
    return CAMERAS


def listar_proporcoes():
    return PROPORCOES


# ============================================================
# TOKEN
# ============================================================

def obter_token_huggingface():
    """
    Procura o token do Hugging Face no ambiente.

    No Streamlit Cloud:
        Settings -> Secrets

    Nome recomendado:
        HF_TOKEN
    """

    token = os.getenv("HF_TOKEN")

    if not token:
        token = os.getenv("HUGGINGFACE_TOKEN")

    return token


# ============================================================
# VERIFICAÇÃO
# ============================================================

def verificar_huggingface():
    """
    Verifica se existe token configurado.
    """

    token = obter_token_huggingface()

    if not token:
        return {
            "ok": False,
            "erro": (
                "HF_TOKEN não configurado."
            ),
        }

    return {
        "ok": True,
        "mensagem": "Hugging Face configurado.",
    }


# ============================================================
# PROMPT DE MOVIMENTO
# ============================================================

def montar_prompt_movimento(
    movimento: str,
    camera: str = "Sony FX6",
):
    """
    Transforma a descrição simples do usuário
    em uma descrição mais adequada para Image-to-Video.
    """

    return f"""
Animate the provided image into a realistic cinematic video.

SUBJECT MOTION:
{movimento}

CAMERA:
{camera}

IMPORTANT:

- Preserve the exact identity of the subject.
- Preserve the face and facial structure.
- Preserve clothing.
- Preserve hairstyle.
- Preserve body proportions.
- Preserve colors and accessories.
- Do not create another character.
- Do not change the subject's identity.
- Keep the original environment consistent.
- Natural realistic movement.
- Smooth cinematic camera movement.
- Realistic lighting.
- Natural physics.
- No sudden scene changes.
- No duplicated body parts.
- No extra fingers.
- No distorted face.
- No melting objects.
- No text or subtitles.

The input image is the visual reference.
Animate the scene instead of replacing the subject.
""".strip()


# ============================================================
# IMAGE -> VIDEO
# ============================================================

def gerar_video_huggingface(
    imagem,
    movimento: str,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    nome_arquivo: str = "video_i2v.mp4",
):
    """
    Gera vídeo a partir de uma imagem.

    imagem:
        arquivo enviado pelo Streamlit
        ou caminho de arquivo.

    movimento:
        descrição do que deve acontecer na cena.
    """

    token = obter_token_huggingface()

    if not token:
        raise RuntimeError(
            "HF_TOKEN não configurado no Streamlit Secrets."
        )

    try:
        from huggingface_hub import InferenceClient

    except ImportError:
        raise RuntimeError(
            "huggingface_hub não está instalado."
        )

    # --------------------------------------------------------
    # SALVA A IMAGEM TEMPORARIAMENTE
    # --------------------------------------------------------

    arquivo_imagem = Path(
        "imagem_referencia_i2v"
    )

    if hasattr(imagem, "read"):

        dados = imagem.read()

        nome_original = getattr(
            imagem,
            "name",
            "imagem.png"
        )

        extensao = Path(
            nome_original
        ).suffix or ".png"

        arquivo_imagem = Path(
            "imagem_referencia_i2v" + extensao
        )

        arquivo_imagem.write_bytes(
            dados
        )

    elif isinstance(
        imagem,
        (str, Path)
    ):

        arquivo_imagem = Path(imagem)

    else:

        raise TypeError(
            "A imagem precisa ser um arquivo enviado "
            "ou um caminho de arquivo."
        )

    if not arquivo_imagem.exists():

        raise RuntimeError(
            "A imagem de referência não foi encontrada."
        )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = montar_prompt_movimento(
        movimento=movimento,
        camera=camera,
    )

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    modelo = os.getenv(
        "HF_VIDEO_MODEL",
        "Wan-AI/Wan2.1-I2V-14B-480P-diffusers"
    )

    # --------------------------------------------------------
    # CLIENTE
    # --------------------------------------------------------

    client = InferenceClient(
        provider="hf-inference",
        api_key=token,
    )

    # --------------------------------------------------------
    # GERAÇÃO
    # --------------------------------------------------------

    try:

        with open(
            arquivo_imagem,
            "rb"
        ) as arquivo:

            video_bytes = client.image_to_video(
                image=arquivo,
                prompt=prompt,
                model=modelo,
            )

    except Exception as erro:

        raise RuntimeError(
            "Erro no motor Hugging Face "
            f"Image-to-Video:\n{erro}"
        )

    # --------------------------------------------------------
    # VALIDA RESULTADO
    # --------------------------------------------------------

    if video_bytes is None:

        raise RuntimeError(
            "O Hugging Face não retornou vídeo."
        )

    # --------------------------------------------------------
    # SALVA VÍDEO
    # --------------------------------------------------------

    caminho = (
        PASTA_VIDEOS /
        nome_arquivo
    )

    try:

        if isinstance(
            video_bytes,
            bytes
        ):

            caminho.write_bytes(
                video_bytes
            )

        elif hasattr(
            video_bytes,
            "read"
        ):

            caminho.write_bytes(
                video_bytes.read()
            )

        else:

            caminho.write_bytes(
                bytes(video_bytes)
            )

    except Exception as erro:

        raise RuntimeError(
            f"Erro salvando o vídeo: {erro}"
        )

    if not caminho.exists():

        raise RuntimeError(
            "O arquivo de vídeo não foi criado."
        )

    if caminho.stat().st_size == 0:

        raise RuntimeError(
            "O vídeo retornado está vazio."
        )

    return str(caminho)


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def gerar_video(
    imagem,
    movimento: str,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    duracao: int = 5,
    nome_arquivo: str = "video.mp4",
):
    """
    Função principal do Alex IA.

    Recebe:
        imagem
        descrição do movimento

    Retorna:
        informações do vídeo gerado.
    """

    if not movimento.strip():

        raise ValueError(
            "Descreva o movimento que deve acontecer."
        )

    caminho = gerar_video_huggingface(
        imagem=imagem,
        movimento=movimento,
        camera=camera,
        proporcao=proporcao,
        nome_arquivo=nome_arquivo,
    )

    return {
        "sucesso": True,
        "motor": "Hugging Face",
        "caminho": caminho,
        "movimento": movimento,
        "camera": camera,
        "proporcao": proporcao,
        "duracao": duracao,
    }


# ============================================================
# TESTE DO MÓDULO
# ============================================================

if __name__ == "__main__":

    print("🎬 Alex IA Ultra")
    print("Gerador Image-to-Video")
    print()
    print(
        "Motores:",
        listar_motores()
    )
    print(
        "Câmeras:",
        listar_cameras()
    )
    print(
        "Proporções:",
        listar_proporcoes()
    )
    print()
    print(
        "✅ video.py carregado corretamente."
    )
