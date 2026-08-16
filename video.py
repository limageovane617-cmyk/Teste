import os
from pathlib import Path
import requests


PASTA_VIDEOS = Path("videos")
PASTA_VIDEOS.mkdir(exist_ok=True)

MOTORES_VIDEO = [
    "Kling 2.1 — Replicate"
]

CAMERAS = [
    "Sony FX5",
    "Sony FX6",
    "Canon EOS C80",
    "ARRI Alexa Mini LF"
]

PROPORCOES = [
    "16:9",
    "9:16",
    "1:1"
]


def listar_motores():
    return MOTORES_VIDEO


def listar_cameras():
    return CAMERAS


def listar_proporcoes():
    return PROPORCOES


def obter_token_replicate():

    token = os.getenv("REPLICATE_API_TOKEN")

    if not token:
        raise RuntimeError(
            "REPLICATE_API_TOKEN não foi encontrado."
        )

    return token


def montar_prompt(movimento, camera):

    return f"""
Animate the provided image into a realistic cinematic video.

Movement:
{movimento}

Camera:
{camera}

Keep the exact same character from the reference image.

Preserve:
- face
- hairstyle
- clothing
- body
- accessories
- colors
- identity

Do not create another character.

Do not change the clothes.

Do not change the face.

Do not duplicate the character.

Use natural realistic movement.

Smooth cinematic camera movement.

Realistic lighting and physics.

The image is the visual reference.
"""


def gerar_video_replicate(
    imagem,
    movimento,
    camera="Sony FX6",
    proporcao="16:9",
    duracao=5,
    nome_arquivo="video_kling.mp4"
):

    token = obter_token_replicate()

    prompt = montar_prompt(
        movimento,
        camera
    )

    # --------------------------------------------------------
    # SALVA A IMAGEM
    # --------------------------------------------------------

    if hasattr(imagem, "getvalue"):

        imagem_bytes = imagem.getvalue()

    elif isinstance(imagem, bytes):

        imagem_bytes = imagem

    else:

        with open(imagem, "rb") as arquivo:
            imagem_bytes = arquivo.read()

    # --------------------------------------------------------
    # CONVERTE PARA DATA URL
    # --------------------------------------------------------

    import base64

    imagem_base64 = base64.b64encode(
        imagem_bytes
    ).decode("utf-8")

    nome = getattr(
        imagem,
        "name",
        "imagem.jpg"
    )

    if nome.lower().endswith(".png"):
        mime = "image/png"
    elif nome.lower().endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    imagem_url = (
        f"data:{mime};base64,{imagem_base64}"
    )

    # --------------------------------------------------------
    # REPLICATE
    # --------------------------------------------------------

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    dados = {
        "input": {
            "prompt": prompt,
            "start_image": imagem_url,
            "duration": 5,
            "aspect_ratio": proporcao
        }
    }

    # Modelo Kling 2.1
    url = (
        "https://api.replicate.com/v1/models/"
        "kwaivgi/kling-v2.1/predictions"
    )

    resposta = requests.post(
        url,
        headers=headers,
        json=dados,
        timeout=60
    )

    if resposta.status_code >= 400:

        raise RuntimeError(
            "Erro ao iniciar o Replicate:\n"
            + resposta.text
        )

    operacao = resposta.json()

    prediction_url = operacao.get(
        "urls",
        {}
    ).get(
        "get"
    )

    if not prediction_url:

        raise RuntimeError(
            "O Replicate não retornou "
            "a URL da operação."
        )

    # --------------------------------------------------------
    # AGUARDA
    # --------------------------------------------------------

    for _ in range(120):

        resposta = requests.get(
            prediction_url,
            headers={
                "Authorization":
                    f"Bearer {token}"
            },
            timeout=60
        )

        if resposta.status_code >= 400:

            raise RuntimeError(
                "Erro consultando Replicate:\n"
                + resposta.text
            )

        resultado = resposta.json()

        status = resultado.get(
            "status"
        )

        if status == "succeeded":
            break

        if status in [
            "failed",
            "canceled"
        ]:

            erro = resultado.get(
                "error",
                "Erro desconhecido."
            )

            raise RuntimeError(
                f"Geração falhou: {erro}"
            )

        import time
        time.sleep(3)

    else:

        raise RuntimeError(
            "O Replicate demorou demais."
        )

    # --------------------------------------------------------
    # PEGA VÍDEO
    # --------------------------------------------------------

    saida = resultado.get(
        "output"
    )

    if not saida:

        raise RuntimeError(
            "O Replicate terminou sem retornar vídeo."
        )

    if isinstance(saida, list):

        video_url = saida[0]

    else:

        video_url = saida

    # --------------------------------------------------------
    # BAIXA VÍDEO
    # --------------------------------------------------------

    caminho = (
        PASTA_VIDEOS /
        nome_arquivo
    )

    video_resposta = requests.get(
        video_url,
        timeout=180
    )

    if video_resposta.status_code != 200:

        raise RuntimeError(
            "Não foi possível baixar o vídeo."
        )

    caminho.write_bytes(
        video_resposta.content
    )

    if caminho.stat().st_size == 0:

        raise RuntimeError(
            "O vídeo baixado está vazio."
        )

    return str(caminho)


def gerar_video(
    imagem,
    movimento,
    camera="Sony FX6",
    proporcao="16:9",
    duracao=5,
    nome_arquivo="video.mp4"
):

    caminho = gerar_video_replicate(
        imagem=imagem,
        movimento=movimento,
        camera=camera,
        proporcao=proporcao,
        duracao=duracao,
        nome_arquivo=nome_arquivo
    )

    return {
        "sucesso": True,
        "motor": "Kling 2.1 — Replicate",
        "caminho": caminho
    }
