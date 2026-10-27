# -*- coding: utf-8 -*-
"""Módulo de Entrada: Captura de áudio do microfone via utilitário ALSA (arecord)."""

import subprocess

DURACAO_PADRAO = 4
TAXA_AMOSTRAGEM = "16000"
CANAL = "1"
FORMATO = "S16_LE"
DISPOSITIVO = "default"


def gravar_audio(output_filename, duracao=DURACAO_PADRAO):
    """Grava o áudio usando o utilitário nativo do Linux (arecord).

    Parâmetros:
        output_filename (str): Caminho do arquivo WAV de saída.
        duracao (int): Duração da gravação em segundos.

    Retorna:
        bool: True se a gravação foi concluída com sucesso, False em caso de falha.
    """
    print("[*] Gravando... Fale o comando agora!")

    comando = [
        "arecord",
        "-D", DISPOSITIVO,       # Usa o microfone padrão ALSA
        "-d", str(duracao),      # Duração em segundos
        "-f", FORMATO,           # Formato 16-bit (exigido pelo Whisper)
        "-r", TAXA_AMOSTRAGEM,   # Taxa de amostragem 16kHz
        "-c", CANAL,             # Mono
        "-q",                    # Modo silencioso (sem poluir o terminal)
        output_filename
    ]

    try:
        codigo_retorno = subprocess.call(comando)
        if codigo_retorno == 0:
            print("[*] Gravacao concluida.")
            return True
        else:
            print("[-] arecord encerrou com codigo: {}".format(codigo_retorno))
            return False
    except Exception as e:
        print("[-] Erro ao gravar audio via arecord: {}".format(e))
        return False
