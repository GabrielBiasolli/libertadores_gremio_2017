# -*- coding: utf-8 -*-
"""Código Principal (main.py): Orquestrador do fluxo Entrada -> Processamento -> Saída."""

import os
import sys

from entrada import gravar_audio
from processamento import obter_chave_api, transcrever_audio, interpretar_comando
from saida import inicializar_robo, executar_acao_yanshee, resetar_robo

# --- CONFIGURAÇÕES DO SISTEMA ---
AUDIO_FILE = "temp_command.wav"
RECORD_SECONDS = 4
ROBOT_IP = "127.0.0.1"


def verificar_requisitos():
    """Valida as configurações obrigatórias antes da execução."""
    if not obter_chave_api():
        print("[-] ERRO: A variavel de ambiente OPENAI_API_KEY nao foi definida.")
        print("    Configure com: export OPENAI_API_KEY=\"sk-...\"")
        sys.exit(1)


def main():
    print("=" * 55)
    print(" YANSHEE VOICE CONTROLLER (Python 3.5+)")
    print(" Pipeline: Entrada (arecord) -> Processamento (IA) -> Saida (YanAPI)")
    print(" Comandos suportados: Andar | Parar | Flexao")
    print("=" * 55)

    verificar_requisitos()
    inicializar_robo(ROBOT_IP)

    try:
        while True:
            entrada_terminal = input("\nPressione [ENTER] para falar (ou 'q' para sair): ")
            if entrada_terminal.strip().lower() == "q":
                break

            # 1. ENTRADA: Captura de áudio do microfone
            gravou = gravar_audio(AUDIO_FILE, duracao=RECORD_SECONDS)
            if not gravou:
                print("[-] Falha na gravacao de audio. Tente novamente.")
                continue

            # 2. PROCESSAMENTO: Transcrição (Whisper) e Classificação (LLM)
            print("[*] Transcrevendo via Whisper...")
            transcricao = transcrever_audio(AUDIO_FILE)
            if not transcricao:
                print("[-] Nenhum audio compreendido.")
                continue

            print("[+] Ouvido: \"{}\"".format(transcricao))

            print("[*] Classificando intencao...")
            acao = interpretar_comando(transcricao)
            print("[+] Acao mapeada: {}".format(acao))

            # 3. SAÍDA: Atuação e movimento no robô
            executar_acao_yanshee(acao)

    except KeyboardInterrupt:
        print("\n[!] Encerrando execucao por interrupcao do usuario.")
    finally:
        # Limpeza de arquivos temporários e postura de segurança do robô
        if os.path.exists(AUDIO_FILE):
            try:
                os.remove(AUDIO_FILE)
            except Exception:
                pass
        resetar_robo()
        print("[*] Recursos liberados e robo em postura de repouso.")


if __name__ == "__main__":
    main()
