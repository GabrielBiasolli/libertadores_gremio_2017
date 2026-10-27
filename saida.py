# -*- coding: utf-8 -*-
"""Módulo de Saída: Atuação física e controle de movimentação no robô Yanshee via YanAPI."""

try:
    import YanAPI
except ImportError:
    YanAPI = None


def inicializar_robo(ip="127.0.0.1"):
    """Inicializa a comunicação com a API do Robô Yanshee."""
    if YanAPI is not None:
        try:
            YanAPI.yan_api_init(ip)
            print("[*] YanAPI conectada com sucesso em {}".format(ip))
            return True
        except Exception as e:
            print("[-] Erro ao conectar YanAPI: {}".format(e))
            return False
    else:
        print("[!] Aviso: YanAPI nao encontrada no ambiente (modo simulacao).")
        return False


def resetar_robo():
    """Retorna os servos e articulações do robô para a postura de repouso."""
    if YanAPI is not None:
        try:
            YanAPI.sync_do_motion_reset()
        except Exception as e:
            print("[-] Erro ao resetar movimentos: {}".format(e))


def executar_acao_yanshee(acao):
    """Executa a movimentação correspondente no Yanshee via YanAPI.

    Parâmetros:
        acao (str): Intenção classificada ('andar', 'parar', 'flexao', etc).
    """
    print("[>] Executando no Yanshee: {}".format(acao))

    if YanAPI is None:
        print("[!] YanAPI ausente: acao '{}' simulada com sucesso.".format(acao))
        return

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
            if "push" in str(mov).lower():  # Busca ignorando maiusculas/minusculas
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
