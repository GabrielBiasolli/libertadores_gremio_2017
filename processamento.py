# -*- coding: utf-8 -*-
"""Módulo de Processamento: Transcrição de áudio (Whisper) e classificação de intenções (LLM).

Compatível com Python 3.5.3+.
"""

import json
import os
import requests

MODELO_TRANSCRICAO = "whisper-1"
MODELO_LLM = "gpt-4o-mini"
URL_TRANSCRICAO = "https://api.openai.com/v1/audio/transcriptions"
URL_COMPLETIONS = "https://api.openai.com/v1/chat/completions"

PROMPT_SISTEMA = (
    "Voce eh o interpretador de comandos de um robo humanoide Yanshee. "
    "Classifique a intencao do usuario estritamente em uma das seguintes palavras: "
    "'andar', 'parar', 'flexao' ou 'desconhecido'. "
    "Responda APENAS com a palavra da acao, sem pontuacao ou texto extra."
)


def carregar_env(nome_arquivo=".env"):
    """Carrega variáveis simples de um arquivo .env se não estiverem definidas no ambiente.

    Verifica tanto no diretório de execução atual quanto no diretório do script.
    Compatível com Python 3.5.3 (sem dependência de python-dotenv).
    """
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        nome_arquivo,
        os.path.join(diretorio_script, nome_arquivo)
    ]

    for caminho in candidatos:
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    for linha in f:
                        linha = linha.strip()
                        if not linha or linha.startswith("#") or "=" not in linha:
                            continue
                        chave, valor = linha.split("=", 1)
                        chave = chave.strip()
                        valor = valor.strip().strip("\"'").strip()
                        if chave and chave not in os.environ:
                            os.environ[chave] = valor
                return
            except Exception:
                pass


def obter_chave_api():
    """Retorna a chave da OpenAI a partir da variável de ambiente ou do arquivo .env."""
    carregar_env()
    return os.environ.get("OPENAI_API_KEY")


def transcrever_audio(audio_path, api_key=None):
    """Envia o áudio gravado para o Whisper via API REST da OpenAI.

    Parâmetros:
        audio_path (str): Caminho do arquivo WAV a transcrever.
        api_key (str, opcional): Chave da OpenAI. Se omitida, busca em os.environ ou .env.

    Retorna:
        str ou None: Texto transcrito ou None em caso de falha.
    """
    chave = api_key or obter_chave_api()
    if not chave:
        print("[-] Erro: Chave OPENAI_API_KEY nao definida (configure via .env ou ambiente).")
        return None

    if not os.path.exists(audio_path):
        print("[-] Arquivo de audio nao encontrado: {}".format(audio_path))
        return None

    headers = {
        "Authorization": "Bearer {}".format(chave)
    }

    try:
        nome_arquivo_envio = os.path.basename(audio_path)
        with open(audio_path, "rb") as f:
            files = {
                "file": (nome_arquivo_envio, f, "audio/wav"),
                "model": (None, MODELO_TRANSCRICAO),
                "language": (None, "pt")
            }
            response = requests.post(URL_TRANSCRICAO, headers=headers, files=files, timeout=20)

        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print("[-] Erro Whisper: {} - {}".format(response.status_code, response.text))
            return None
    except Exception as e:
        print("[-] Excecao ao chamar Whisper: {}".format(e))
        return None


def interpretar_comando(texto, api_key=None):
    """Envia a transcrição ao LLM para mapear na intenção do robô.

    Parâmetros:
        texto (str): Texto da fala do usuário.
        api_key (str, opcional): Chave da OpenAI.

    Retorna:
        str: Uma das intenções ('andar', 'parar', 'flexao' ou 'desconhecido').
    """
    chave = api_key or obter_chave_api()
    if not chave:
        print("[-] Erro: Chave OPENAI_API_KEY nao definida (configure via .env ou ambiente).")
        return "desconhecido"

    headers = {
        "Authorization": "Bearer {}".format(chave),
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODELO_LLM,
        "messages": [
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": texto}
        ],
        "temperature": 0.0
    }

    try:
        dados_json = json.dumps(payload).encode("utf-8")
        response = requests.post(URL_COMPLETIONS, headers=headers, data=dados_json, timeout=15)
        if response.status_code == 200:
            resultado = response.json()["choices"][0]["message"]["content"]
            return resultado.strip().lower()
        else:
            print("[-] Erro LLM: {} - {}".format(response.status_code, response.text))
            return "desconhecido"
    except Exception as e:
        print("[-] Excecao ao chamar LLM: {}".format(e))
        return "desconhecido"
