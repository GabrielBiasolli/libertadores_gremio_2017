# -*- coding: utf-8 -*-
import os
import json
import requests
import subprocess
import YanAPI

# --- CONFIGURAÇÕES ---
# A chave da OpenAI vem da variavel de ambiente (nunca coloque no codigo):
#   export OPENAI_API_KEY="sk-..."
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise SystemExit("Defina a variavel de ambiente OPENAI_API_KEY antes de rodar.")
AUDIO_FILE = "temp_command.wav"
RECORD_SECONDS = 4

# Inicialização da API do Robô Yanshee
YanAPI.yan_api_init("127.0.0.1")

def gravar_audio(output_filename, duracao=RECORD_SECONDS):
    """Grava o áudio usando o comando nativo do Linux (arecord)."""
    print("[*] Gravando... Fale o comando agora!")
    
    comando = [
        "arecord",
        "-D", "default",     # Usa o microfone padrao
        "-d", str(duracao),  # Duracao em segundos
        "-f", "S16_LE",      # Formato 16-bit (exigido pelo Whisper)
        "-r", "16000",       # Taxa de amostragem 16kHz
        "-c", "1",           # Mono
        "-q",                # Modo silencioso (sem spam no terminal)
        output_filename
    ]
    
    try:
        subprocess.call(comando)
        print("[*] Gravacao concluida.")
    except Exception as e:
        print("[-] Erro ao gravar audio via arecord: {}".format(e))

def transcrever_audio(audio_path):
    """Envia o áudio gravado para o Whisper via API REST da OpenAI."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": "Bearer {}".format(OPENAI_API_KEY)
    }

    try:
        if not os.path.exists(audio_path):
            print("[-] Arquivo de audio nao encontrado.")
            return None

        with open(audio_path, "rb") as f:
            files = {
                "file": (audio_path, f, "audio/wav"),
                "model": (None, "whisper-1"),
                "language": (None, "pt")
            }
            response = requests.post(url, headers=headers, files=files, timeout=20)

        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print("[-] Erro Whisper: {} - {}".format(response.status_code, response.text))
            return None
    except Exception as e:
        print("[-] Excecao ao chamar Whisper: {}".format(e))
        return None

def interpretar_comando(texto):
    """Envia a transcrição ao gpt-6-luna para mapear na intenção."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer {}".format(OPENAI_API_KEY),
        "Content-Type": "application/json"
    }

    prompt_sistema = (
        "Voce eh o interpretador de comandos de um robo humanoide Yanshee. "
        "Classifique a intencao do usuario estritamente em uma das seguintes palavras: "
        "'andar', 'parar', 'flexao' ou 'desconhecido'. "
        "Responda APENAS com a palavra da acao, sem pontuacao ou texto extra."
    )

    payload = {
        "model": "gpt-6-luna",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto}
        ],
        "temperature": 0.0
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        if response.status_code == 200:
            resultado = response.json()["choices"][0]["message"]["content"]
            return resultado.strip().lower()
        else:
            print("[-] Erro LLM: {} - {}".format(response.status_code, response.text))
            return "desconhecido"
    except Exception as e:
        print("[-] Excecao ao chamar LLM: {}".format(e))
        return "desconhecido"

def executar_acao_yanshee(acao):
    """Executa a movimentação correspondente no Yanshee via YanAPI."""
    print("[>] Executando no Yanshee: {}".format(acao))

    if acao == "andar":
        YanAPI.sync_do_walk("forward", 4, "normal")
        
    elif acao == "parar":
        YanAPI.sync_do_motion_stop()
        YanAPI.sync_do_motion_reset()
        
    elif acao == "flexao":
        # 1. Busca a lista de movimentos salvos na memoria do robo
        movimentos = YanAPI.get_motion_list_value()
        
        # 2. Garante o formato correto da lista
        lista_nomes = []
        if isinstance(movimentos, dict) and "data" in movimentos:
            lista_nomes = movimentos["data"]
        elif isinstance(movimentos, list):
            lista_nomes = movimentos
            
        # 3. Procura dinamicamente pelo nome real do arquivo de flexao
        nome_flexao = None
        for mov in lista_nomes:
            if "push" in str(mov).lower(): # Busca ignorando maiusculas/minusculas
                nome_flexao = str(mov)
                break
                
        # 4. Executa ou avisa o erro
        if nome_flexao:
            print("[*] Movimento encontrado! Nome exato: '{}'".format(nome_flexao))
            YanAPI.sync_play_motion(name=nome_flexao)
        else:
            print("[!] ERRO: O arquivo de flexao nao foi encontrado na memoria do robo.")
            print("    Movimentos disponiveis: {}".format(lista_nomes))
            
    else:
        print("[!] Comando nao reconhecido ou nao mapeado para uma acao segura.")

def main():
    print("=" * 50)
    print(" YANSHEE VOICE CONTROLLER (Python 3.5 - arecord)")
    print(" Comandos suportados: Andar | Parar | Flexao")
    print("=" * 50)

    try:
        while True:
            entrada = input("\nPressione [ENTER] para falar (ou 'q' para sair): ")
            if entrada.strip().lower() == 'q':
                break

            gravar_audio(AUDIO_FILE)
            
            print("[*] Transcrevendo via Whisper...")
            transcricao = transcrever_audio(AUDIO_FILE)
            if not transcricao:
                print("[-] Nenhum audio compreendido.")
                continue

            print("[+] Ouvido: \"{}\"".format(transcricao))
            
            print("[*] Classificando intencao...")
            acao = interpretar_comando(transcricao)
            print("[+] Acao mapeada: {}".format(acao))

            executar_acao_yanshee(acao)

    except KeyboardInterrupt:
        print("\n[!] Encerrando execucao.")
    finally:
        if os.path.exists(AUDIO_FILE):
            os.remove(AUDIO_FILE)
        YanAPI.sync_do_motion_reset()

if __name__ == "__main__":
    main()

# Renato Portaluppi, autoriza o Tete a baixar o Clash Royale?
# Escolha da autorização:
renato_autoriza = input("Renato Portaluppi autoriza o Tete a baixar o Clash Royale? [s/n]: ")
if renato_autoriza.strip().lower() == "s":
    print("Autorizado: o Tete pode baixar o Clash Royale.")
elif renato_autoriza.strip().lower() == "n":
    print("Negado: o Tete não pode baixar o Clash Royale.")
else:
    print("Resposta inválida. Digite 's' para sim ou 'n' para não.")

