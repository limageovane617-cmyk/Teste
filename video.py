# video.py
# Teste mínimo do módulo de vídeo

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


def listar_motores():
    return MOTORES_VIDEO


def listar_cameras():
    return CAMERAS


def gerar_video(*args, **kwargs):
    return {
        "sucesso": False,
        "motor": None,
        "caminho": None,
        "erros": [
            "Sistema de vídeo em modo de teste."
        ],
    }
