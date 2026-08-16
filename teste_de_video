"""
Alex IA Ultra — Gerenciador de geração de vídeos
Sistema de múltiplos motores com fallback automático.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_VIDEOS = Path(os.getenv("VIDEO_OUTPUT_DIR", "videos"))
PASTA_VIDEOS.mkdir(parents=True, exist_ok=True)

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

# Ordem do fallback
MOTORES_VIDEO = [
    "Veo",
    "Replicate",
    "Hugging Face",
]


# ============================================================
# UTILITÁRIOS
# ============================================================

def _nome_seguro(nome: str) -> str:
    permitido = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    resultado = "".join(
        c if c in permitido else "_"
        for c in str(nome)
    )

    return resultado.strip("_") or "video"


def _tem_env(*nomes: str) -> bool:
    return any(
        os.getenv(nome, "").strip()
        for nome in nomes
    )


def _resultado_valido(resultado: Any) -> bool:

    if resultado is None:
        return False

    if isinstance(resultado, (bytes, bytearray)):
        return len(resultado) > 0

    if isinstance(resultado, str):
        return bool(resultado.strip())

    if isinstance(resultado, Path):
        return resultado.exists()

    if isinstance(resultado, dict):

        for chave in (
            "video_path",
            "path",
            "url",
            "video_url",
            "file",
        ):
            if resultado.get(chave):
                return True

    return True


# ============================================================
# PROMPT DO VÍDEO
# ============================================================

def montar_prompt_video(
    descricao: str,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    duracao: int = DURACAO_PADRAO,
) -> str:

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

- manter exatamente o mesmo personagem durante todo o vídeo;
- manter rosto, cabelo, corpo, roupa e acessórios consistentes;
- se a câmera sair do personagem, quando retornar deve mostrar
  exatamente o mesmo personagem;
- não trocar roupa;
- não trocar rosto;
- não criar uma segunda versão do personagem;
- manter o mesmo cenário e iluminação;
- movimentos naturais;
- movimento de câmera cinematográfico;
- evitar deformações;
- evitar duplicação do personagem;
- evitar mudanças repentinas.

ESTILO:

cinematográfico,
realista,
alta qualidade,
movimento de câmera suave.
""".strip()


# ============================================================
# MOTOR VEO / GEMINI
# ============================================================

def gerar_com_veo(
    prompt: str,
    duracao: int = DURACAO_PADRAO,
    proporcao: str = "16:9",
    nome_arquivo: str = "video_veo.mp4",
) -> Optional[str]:

    chave = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not chave:
        raise RuntimeError(
            "GEMINI_API_KEY/GOOGLE_API_KEY não configurada."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "Biblioteca google-genai não instalada."
        ) from exc

    client = genai.Client(api_key=chave)

    modelo = os.getenv(
        "VEO_MODEL",
        "veo-3.1-generate-preview"
    )

    try:

        operacao = client.models.generate_videos(
            model=modelo,
            prompt=prompt,
            config={
                "duration_seconds": duracao,
                "aspect_ratio": proporcao,
            },
        )

    except TypeError:

        operacao = client.models.generate_videos(
            model=modelo,
            prompt=prompt,
        )

    limite = int(
        os.getenv(
            "VIDEO_POLL_LIMIT",
            "60"
        )
    )

    for _ in range(limite):

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
            "Veo não terminou a geração dentro do tempo limite."
        )

    resposta = (
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

    candidatos = []

    if resposta is not None:

        candidatos.append(resposta)

        videos = getattr(
            resposta,
            "generated_videos",
            None
        )

        if videos:
            candidatos.extend(videos)

        videos = getattr(
            resposta,
            "videos",
            None
        )

        if videos:
            candidatos.extend(videos)

    for item in candidatos:

        arquivo = (
            getattr(
                item,
                "video",
                None
            )
            or item
        )

        nome = getattr(
            arquivo,
            "name",
            None
        )

        if nome:

            try:

                caminho = (
                    PASTA_VIDEOS /
                    _nome_seguro(nome_arquivo)
                )

                client.files.download(
                    file=arquivo,
                    path=str(caminho)
                )

                if (
                    caminho.exists()
                    and caminho.stat().st_size > 0
                ):
                    return str(caminho)

            except Exception:
                pass

        dados = getattr(
            arquivo,
            "data",
            None
        )

        if isinstance(
            dados,
            (bytes, bytearray)
        ):

            caminho = (
                PASTA_VIDEOS /
                _nome_seguro(nome_arquivo)
            )

            caminho.write_bytes(dados)

            return str(caminho)

    raise RuntimeError(
        "Veo respondeu, mas não foi possível obter o arquivo."
    )


# ============================================================
# MOTOR REPLICATE
# ============================================================

def gerar_com_replicate(
    prompt: str,
    duracao: int = DURACAO_PADRAO,
    proporcao: str = "16:9",
    nome_arquivo: str = "video_replicate.mp4",
) -> Optional[str]:

    token = os.getenv(
        "REPLICATE_API_TOKEN"
    )

    if not token:
        raise RuntimeError(
            "REPLICATE_API_TOKEN não configurado."
        )

    modelo = os.getenv(
        "REPLICATE_VIDEO_MODEL"
    )

    if not modelo:
        raise RuntimeError(
            "REPLICATE_VIDEO_MODEL não configurado."
        )

    try:
        import replicate
    except ImportError as exc:
        raise RuntimeError(
            "Biblioteca replicate não instalada."
        ) from exc

    entrada = {
        "prompt": prompt
    }

    if os.getenv(
        "REPLICATE_SEND_DURATION",
        "0"
    ) == "1":

        entrada["duration"] = duracao

    if os.getenv(
        "REPLICATE_SEND_ASPECT_RATIO",
        "0"
    ) == "1":

        entrada["aspect_ratio"] = proporcao

    resultado = replicate.run(
        modelo,
        input=entrada
    )

    if not _resultado_valido(resultado):
        raise RuntimeError(
            "Replicate não retornou um vídeo válido."
        )

    caminho = (
        PASTA_VIDEOS /
        _nome_seguro(nome_arquivo)
    )

    if isinstance(
        resultado,
        (bytes, bytearray)
    ):

        caminho.write_bytes(resultado)

        return str(caminho)

    if isinstance(resultado, str):

        try:

            import requests

            resposta = requests.get(
                resultado,
                timeout=180
            )

            resposta.raise_for_status()

            caminho.write_bytes(
                resposta.content
            )

            return str(caminho)

        except Exception:

            if Path(resultado).exists():

                Path(resultado).replace(
                    caminho
                )

                return str(caminho)

            return resultado

    if hasattr(
        resultado,
        "read"
    ):

        dados = resultado.read()

        if dados:

            caminho.write_bytes(
                dados
            )

            return str(caminho)

    raise RuntimeError(
        "Formato de saída do Replicate não reconhecido."
    )


# ============================================================
# MOTOR HUGGING FACE
# ============================================================

def gerar_com_huggingface(
    prompt: str,
    duracao: int = DURACAO_PADRAO,
    proporcao: str = "16:9",
    nome_arquivo: str = "video_huggingface.mp4",
) -> Optional[str]:

    token = (
        os.getenv("HF_TOKEN")
        or
        os.getenv(
            "HUGGINGFACEHUB_API_TOKEN"
        )
    )

    if not token:
        raise RuntimeError(
            "HF_TOKEN não configurado."
        )

    modelo = os.getenv(
        "HF_VIDEO_MODEL"
    )

    if not modelo:
        raise RuntimeError(
            "HF_VIDEO_MODEL não configurado."
        )

    try:

        from huggingface_hub import (
            InferenceClient
        )

    except ImportError as exc:

        raise RuntimeError(
            "Biblioteca huggingface_hub não instalada."
        ) from exc

    client = InferenceClient(
        token=token
    )

    try:

        resultado = client.text_to_video(
            prompt=prompt,
            model=modelo,
        )

    except TypeError:

        resultado = client.text_to_video(
            prompt,
            model=modelo
        )

    if not resultado:

        raise RuntimeError(
            "Hugging Face não retornou vídeo."
        )

    caminho = (
        PASTA_VIDEOS /
        _nome_seguro(nome_arquivo)
    )

    if isinstance(
        resultado,
        (bytes, bytearray)
    ):

        caminho.write_bytes(
            resultado
        )

        return str(caminho)

    if hasattr(
        resultado,
        "read"
    ):

        dados = resultado.read()

        if dados:

            caminho.write_bytes(
                dados
            )

            return str(caminho)

    raise RuntimeError(
        "Formato de saída do Hugging Face não reconhecido."
    )


# ============================================================
# FALLBACK AUTOMÁTICO
# ============================================================

def gerar_video(
    descricao: str,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    duracao: int = DURACAO_PADRAO,
    nome_arquivo: str = "video.mp4",
    motores: Optional[List[str]] = None,
) -> Dict[str, Any]:

    if not descricao or not str(
        descricao
    ).strip():

        return {
            "sucesso": False,
            "motor": None,
            "caminho": None,
            "erros": [
                "Descrição do vídeo vazia."
            ],
        }

    if proporcao not in PROPORCOES:
        proporcao = "16:9"

    try:

        duracao = max(
            1,
            int(duracao)
        )

    except Exception:

        duracao = DURACAO_PADRAO

    prompt = montar_prompt_video(
        descricao=descricao,
        camera=camera,
        proporcao=proporcao,
        duracao=duracao,
    )

    disponiveis: Dict[
        str,
        Callable[..., Optional[str]]
    ] = {

        "Veo": gerar_com_veo,

        "Replicate": gerar_com_replicate,

        "Hugging Face": gerar_com_huggingface,
    }

    ordem = motores or MOTORES_VIDEO

    erros = []

    for motor in ordem:

        funcao = disponiveis.get(
            motor
        )

        if funcao is None:

            erros.append(
                f"{motor}: motor desconhecido."
            )

            continue

        try:

            caminho = funcao(
                prompt=prompt,
                duracao=duracao,
                proporcao=proporcao,
                nome_arquivo=nome_arquivo,
            )

            if caminho:

                return {
                    "sucesso": True,
                    "motor": motor,
                    "caminho": str(caminho),
                    "prompt": prompt,
                    "erros": erros,
                }

            erros.append(
                f"{motor}: não retornou caminho do vídeo."
            )

        except Exception as exc:

            mensagem = (
                str(exc)
                .replace("\n", " ")
                .strip()
            )

            erros.append(
                f"{motor}: {mensagem}"
            )

    return {
        "sucesso": False,
        "motor": None,
        "caminho": None,
        "prompt": prompt,
        "erros": erros,
    }


# ============================================================
# COMPATIBILIDADE
# ============================================================

def gerar_video_fallback(
    descricao: str,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    duracao: int = DURACAO_PADRAO,
    nome_arquivo: str = "video.mp4",
) -> Dict[str, Any]:

    return gerar_video(
        descricao=descricao,
        camera=camera,
        proporcao=proporcao,
        duracao=duracao,
        nome_arquivo=nome_arquivo,
    )


def listar_motores() -> List[str]:
    return list(MOTORES_VIDEO)


def listar_cameras() -> List[str]:
    return list(CAMERAS)


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    print(
        "=== Alex IA Ultra — Gerenciador de vídeo ==="
    )

    print(
        "Motores:",
        ", ".join(MOTORES_VIDEO)
    )

    print(
        "Câmeras:",
        ", ".join(CAMERAS)
    )

    print(
        "Duração padrão:",
        DURACAO_PADRAO,
        "segundos"
    )

    print(
        "Proporções:",
        ", ".join(PROPORCOES)
    )

    print(
        "\nFallback pronto."
    )
