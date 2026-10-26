# Controle por Voz - Robô UBTECH Yanshee

## 1. Finalidade

Script em Python para controle por voz do robô humanóide **UBTECH Yanshee**. O sistema captura áudio localmente, transcreve a fala via API OpenAI Whisper, classifica a intenção do comando através de um modelo de linguagem (LLM) e dispara a movimentação correspondente no robô via `YanAPI`.

---

## 2. Estrutura do Repositório

```text
├── .env                # Variáveis de ambiente locais (ignorado no git)
├── .gitignore          # Arquivos e diretórios ignorados
├── requirements.txt    # Dependência Python (requests)
├── main.py             # Script único de captura, IA e controle
└── README.md           # Esta documentação
```

### Funções no `main.py`:
- `gravar_audio()`: Executa `arecord` no Linux para gravar 4 segundos de áudio em 16kHz mono.
- `transcrever_audio()`: Envia o áudio ao endpoint Whisper (`whisper-1`) em português.
- `interpretar_comando()`: Envia o texto ao LLM para classificar estritamente em: `andar`, `parar`, `flexao` ou `desconhecido`.
- `executar_acao_yanshee()`: Mapeia a intenção classificada para chamadas de movimento na biblioteca `YanAPI`.
- `main()`: Loop interativo no terminal (pressionar `ENTER` para falar, `q` para sair).

---

## 3. Ambiente (Robô UBTECH Yanshee)

- **Plataforma:** Robô humanóide UBTECH Yanshee com placa interna baseada em Raspberry Pi / Linux.
- **Áudio:** Captura de microfone gerenciada pelo subsistema Linux ALSA (`arecord`).
- **SDK do Robô:** Biblioteca Python proprietária `YanAPI` conectada localmente via socket/IPC (`127.0.0.1`).
- **Interpretador:** Python 3 (código formatado para compatibilidade com Python 3.5+).
- **Conectividade:** Exige conexão ativa com a internet para comunicação com as APIs da OpenAI.

---

## 4. Configuração

1. **Dependência Python:**
   ```bash
   pip3 install -r requirements.txt
   ```
   *(Nota: O módulo `YanAPI` é nativo do ambiente do Yanshee).*

2. **Chave de API OpenAI:**
   Definir obrigatoriamente a variável de ambiente:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

3. **Pacote de Áudio do Sistema:**
   O utilitário `arecord` deve estar disponível no PATH do Linux (pacote `alsa-utils`).

---

## 5. Execução

No terminal do Yanshee:

```bash
python3 main.py
```

- Pressione **`ENTER`** para iniciar a gravação de 4 segundos e fale o comando.
- Digite **`q`** e pressione **`ENTER`** (ou use `Ctrl+C`) para sair. Ao encerrar, o áudio temporário é apagado e os motores retornam à posição de repouso (`sync_do_motion_reset`).

### Ações Implementadas:
- **`andar`**: `YanAPI.sync_do_walk("forward", 4, "normal")` (anda 4 passos para frente).
- **`parar`**: `YanAPI.sync_do_motion_stop()` e `YanAPI.sync_do_motion_reset()`.
- **`flexao`**: Busca movimento na memória contendo a substring `"push"` e executa `YanAPI.sync_play_motion(name=...)`.

---

## 6. Limites e Restrições

- **Tempo fixo de escuta:** A gravação é travada em 4 segundos fixos, sem detecção dinâmica de silêncio (VAD).
- **Dependência de internet:** O processamento depende inteiramente da latência e disponibilidade dos servidores da OpenAI.
- **Vocabulário restrito:** Apenas 3 ações físicas estão implementadas (`andar`, `parar`, `flexao`). Qualquer outra fala é categorizada como `desconhecido`.
- **Bloqueio síncrono:** As ações de caminhada e flexão são síncronas (`sync_...`), bloqueando novas entradas até o término do movimento.

---

## 7. Pontos a Confirmar no Hardware Real

- [ ] **Modelo LLM (`gpt-6-luna`):** O código referencia o modelo `"gpt-6-luna"`. É necessário confirmar se a chave utilizada tem acesso a este identificador ou se deve ser alterada para um modelo disponível (ex: `gpt-4o-mini`).
- [ ] **Nome do movimento de flexão:** Confirmar se o arquivo de movimento de flexão instalado na memória do robô contém `"push"` no nome retornado por `YanAPI.get_motion_list_value()`.
- [ ] **Dispositivo de entrada ALSA:** Confirmar se o microfone padrão do robô responde corretamente por `-D default` no `arecord` ou se exige indicar o cartão/dispositivo específico (ex: `-D hw:1,0`).
- [ ] **Níveis de ganho do microfone:** Testar se o nível de volume capturado pelo microfone embutido é suficiente para o Whisper transcrever com precisão no ambiente de teste.
