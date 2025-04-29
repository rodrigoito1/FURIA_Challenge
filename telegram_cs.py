import telebot
import json

# Chave da API do Telegram
chave_api = "8163572933:AAH5r4Ip8ZBVuBOlaqFEH18s-EwzOZ7AxNA"
bot = telebot.TeleBot(chave_api)

# Função para carregar os dados do JSON
def carregarDados():
    with open('dados.json', 'r', encoding='utf-8') as file:
        return json.load(file)

dados = carregarDados()

def menu():
    return (
        "Escolha uma opção:\n"
        "/elenco - Ver elenco do time de CS2\n"
        "/partidas - Próximas partidas\n"
        "/historico - Histórico de partidas\n"
        "/loja - Loja oficial FURIA"
    )

@bot.message_handler(commands=["start", "menu"])
def iniciar(mensagem):
    bot.reply_to(mensagem, f"Bem-vindo ao bot oficial FURIA CS2! 🎯\n\n{menu()}")

@bot.message_handler(commands=["elenco"])
def elenco(mensagem):
    texto = dados['Elenco'].get("CS2", "Elenco não disponível no momento.")
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=["partidas"])
def partidas(mensagem):
    texto = dados['ProxPartidas'].get("CS2", "Próximas partidas não disponíveis.")
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=["historico"])
def historico(mensagem):
    texto = dados['Historico'].get("CS2", "Histórico não disponível.")
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=["loja"])
def loja(mensagem):
    bot.reply_to(mensagem, "Acesse a loja oficial da FURIA: https://www.furia.gg/")

# Mensagem padrão
@bot.message_handler(func=lambda m: True)
def responder(mensagem):
    bot.reply_to(mensagem, f"Use o menu abaixo para explorar informações do time de CS2 🖤\n\n{menu()}")

bot.polling(timeout=60, long_polling_timeout=60)
