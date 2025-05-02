# FURIA_Challenge
# FURIA CS2 Palpites Bot

Bot do Telegram para registrar e gerenciar palpites de partidas do time FURIA de CS2.

## Funcionalidades Principais

* Registro de palpites sobre o placar das partidas.
* Comando de administração para abrir e encerrar palpites.
* Definição de adversário e resultado da partida.
* Verificação automática de acertos com atualização de pontuação.
* Ranking dos maiores pontuadores.
* Informativos sobre elenco, próximas partidas, histórico e loja da FURIA.

## Requisitos

* Python 3.6+
* Biblioteca `pyTelegramBotAPI`

## Instalação

```bash
pip install pyTelegramBotAPI
```

## Executando o bot

1. Clone ou copie este repositório.
2. Insira sua chave de API do Bot do Telegram na variável `chave_api`.
3. Execute o arquivo Python:

```bash
python nome_do_arquivo.py
```

## Estrutura dos arquivos JSON

* `dados.json`: Informativo sobre elenco, partidas, histórico etc.
* `palpites.json`: Registra os palpites dos usuários.
* `resultado_real.json`: Resultado real da partida.
* `pontuacao.json`: Pontuação dos usuários.
* `adversario.json`: Nome do adversário da rodada.
* `status_palpites.json`: Estado (aberto/fechado) dos palpites.

## Comandos do Bot

### Gerais

* `/start` ou `/menu` - Exibe o menu principal.
* `/elenco` - Mostra o elenco da equipe.
* `/partidas` - Exibe as próximas partidas.
* `/historico` - Mostra histórico de partidas.
* `/loja` - Link para a loja oficial da FURIA.
* `/top10` - Mostra os 10 maiores pontuadores.
* `/meuid` - Informa o ID do usuário.

### Palpites

* `/palpites` - Inicia o processo de envio de palpite (se permitido).

### Admin (somente para o ID do ADMIN)

* `/setar_adversario <nome>` - Define o nome do adversário.
* `/abrir_palpites` - Libera envio de palpites.
* `/encerrar_palpites` - Encerra envio de palpites.
* `/definir_resultado <FURIA> <Adversario>` - Define o resultado real da partida e processa os palpites.
* `/verificar_resultado` - Reexecuta a verificação de resultado com base no JSON salvo.

## Observações

* O bot armazena todos os dados em arquivos JSON locais. Para produção, recomenda-se usar um banco de dados.
* Após cada resultado, a pontuação é atualizada e os acertadores são notificados diretamente via Telegram.

---

Criado para interação da comunidade com o time FURIA de CS2. ✨
