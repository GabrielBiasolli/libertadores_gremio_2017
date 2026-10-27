# Controle por Voz - Robô UBTECH Yanshee

## 1. Finalidade

Sistema modular em Python para controle por voz do robô humanóide **UBTECH Yanshee**. O sistema captura comandos de voz localmente via microfone, transcreve a fala por meio da API OpenAI Whisper, classifica a intenção de movimento com um modelo de linguagem (LLM) e dispara os comandos motores correspondentes via `YanAPI`.

O projeto adota princípios de **engenharia de software e arquitetura modular**, separando estritamente as etapas de **Entrada**, **Processamento** e **Saída**, coordenadas pelo script principal **`main.py`**.

---

## 2. Estrutura do Repositório

```text
├── .env.example        # Modelo de variáveis de ambiente (sem chaves sensíveis)
├── .gitignore          # Arquivos e diretórios ignorados (inclui o .env com a chave real)
├── requirements.txt    # Dependência Python compatível com Python 3.5.3+
├── entrada.py          # Código de ENTRADA: captura de áudio do microfone (arecord)
├── processamento.py    # Código de PROCESSAMENTO: IA (Whisper + LLM)
├── saida.py            # Código de SAÍDA: atuação física no robô (YanAPI)
├── main.py             # Código PRINCIPAL: coordenação do pipeline
└── README.md           # Documentação técnica
```

---

## 3. Arquitetura Modular: Entrada, Processamento e Saída

A arquitetura do software é dividida em 3 módulos de responsabilidade única e 1 script orquestrador principal:

```text
               ┌────────────────────────────────────────────────────────┐
               │                        main.py                         │
               │                 (Orquestrador do Fluxo)                │
               └───────────────┬────────────────────────┬───────────────┘
                               │                        │
                               ▼                        ▼
┌──────────────────┐    ┌───────────────┐        ┌──────────────┐        ┌─────────────────┐
│     Usuário      │───▶│   ENTRADA     │───────▶│PROCESSAMENTO │───────▶│      SAÍDA      │───▶ Robô Yanshee
│  (Comando de Voz)│    │ (entrada.py)  │        │(processamento.py)     │   (saida.py)    │     (Motores)
└──────────────────┘    └───────────────┘        └──────────────┘        └─────────────────┘
                          arecord (ALSA)          Whisper + LLM                YanAPI
```

| Módulo | Arquivo | Responsabilidade | Funções Principais |
|---|---|---|---|
| **Entrada** | `entrada.py` | Captura acústica de dados do microfone via utilitário do sistema ALSA. Não toma decisões nem executa ações motoras. | `gravar_audio(output_filename, duracao)` |
| **Processamento** | `processamento.py` | Lógica de inteligência artificial e decisão. Transcreve o áudio em texto e infere a intenção (`andar`, `parar`, `flexao` ou `desconhecido`). Carrega automaticamente a chave do `.env`. | `transcrever_audio(audio_path)`<br>`interpretar_comando(texto)`<br>`obter_chave_api()` |
| **Saída** | `saida.py` | Atuação física e interface com o hardware do robô através da biblioteca `YanAPI`. Possui modo de simulação automático caso executado fora do robô. | `inicializar_robo(ip)`<br>`executar_acao_yanshee(acao)`<br>`resetar_robo()` |
| **Principal** | `main.py` | Orquestração do ciclo de vida: valida o ambiente, inicializa o robô, executa o laço interativo conectando Entrada ➔ Processamento ➔ Saída e garante o reset no encerramento. | `verificar_requisitos()`<br>`main()` |

---

## 4. Ambiente (Robô UBTECH Yanshee)

- **Plataforma:** Robô humanóide UBTECH Yanshee com placa interna baseada em Raspberry Pi 3 (Raspbian Stretch / Debian 9).
- **Interpretador:** Python 3.5.3 nativo (100% suportado sem sintaxe moderna incompatível).
- **Áudio:** Subsistema Linux ALSA com ferramenta `arecord` para gravação de áudio em 16kHz mono.
- **SDK do Robô:** Biblioteca Python proprietária `YanAPI` conectada localmente via socket/IPC (`127.0.0.1`).
- **Conectividade:** Exige acesso à internet para requisições HTTPS às APIs da OpenAI.

---

## 5. Configuração

1. **Dependência Python (no Python 3.5.3 do Yanshee):**
   ```bash
   pip3 install -r requirements.txt
   ```
   *Alternativa nativa no Raspbian (sem necessidade de pip):*
   ```bash
   sudo apt-get install python3-requests
   ```
   *(Nota: O módulo `YanAPI` já vem pré-instalado na imagem oficial do Yanshee).*

2. **Chave de API OpenAI:**
   Crie o arquivo `.env` a partir do modelo `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Abra o `.env` e insira sua chave da OpenAI:
   ```env
   OPENAI_API_KEY=sk-...
   ```
   *(O arquivo `.env` está no `.gitignore` para nunca ser enviado ao GitHub).*

3. **Pacote de Áudio do Sistema:**
   O utilitário `arecord` deve estar disponível no PATH (pacote `alsa-utils` no Linux).

---

## 6. Execução

Execute o **código principal**:

```bash
python3 main.py
```

### Operação Interativa:
1. Pressione **`ENTER`** para iniciar a captura de 4 segundos e fale o comando desejado.
2. O sistema transcreve a fala, classifica a intenção via `gpt-4o-mini` e aciona os atuadores do robô.
3. Para sair, digite **`q`** e pressione **`ENTER`** (ou use `Ctrl+C`). Ao finalizar, o arquivo de áudio temporário é removido e os servos retornam à postura de repouso (`resetar_robo`).

### Comandos de Ação Suportados:
- **`andar`**: `YanAPI.sync_do_walk("forward", 4, "normal")` (avança 4 passos).
- **`parar`**: `YanAPI.sync_do_motion_stop()` seguido de `YanAPI.sync_do_motion_reset()`.
- **`flexao`**: Busca dinamicamente na lista de movimentos instalados o arquivo contendo `"push"` e executa `YanAPI.sync_play_motion()`.

---

## 7. Limites e Restrições

- **Tempo fixo de escuta:** Gravação travada em 4 segundos fixos, sem detecção dinâmica de silêncio (VAD).
- **Dependência de internet:** A etapa de processamento depende da latência e conectividade com os servidores da OpenAI.
- **Vocabulário restrito:** Apenas 3 ações físicas são executadas (`andar`, `parar`, `flexao`). Qualquer comando diferente é categorizado como `desconhecido`.
- **Chamadas síncronas:** Ações de locomoção e flexão bloqueiam o fluxo até a conclusão do movimento.

---

## 8. Pontos a Confirmar no Hardware Real

- [x] **Compatibilidade Python 3.5.3:** Sintaxe rigorosamente verificada e testada sem dependências ou recursos do Python 3.6+.
- [x] **Modelo LLM:** Atualizado para `gpt-4o-mini` em `processamento.py` (modelo oficial de alta velocidade e baixo custo).
- [ ] **Nome do movimento de flexão:** Validar se o nome do arquivo de movimento instalado na memória interna do robô contém `"push"` (`YanAPI.get_motion_list_value()`).
- [ ] **Dispositivo ALSA:** Verificar se o microfone padrão responde por `-D default` ou se requer endereço explícito (ex.: `-D hw:1,0`).
- [ ] **Nível de ganho do microfone:** Ajustar o volume de captura para garantir clareza no Whisper em ambientes com ruído acústico.
