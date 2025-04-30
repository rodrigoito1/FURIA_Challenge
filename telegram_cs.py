import telebot
import json

# Chave da API do Telegram
chave_api = "8163572933:AAH5r4Ip8ZBVuBOlaqFEH18s-EwzOZ7AxNA"
bot = telebot.TeleBot(chave_api)

adversario_nome = "NAVI"
estado_resultado = {}

# Utilitários de JSON
def carregar_json(nome):
    try:
        with open(nome, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def carregarDados():
    return carregar_json("dados.json")

dados = carregarDados()

def carregar_resultado():
    try:
        with open("resultado_real.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# --- /palpites ---
@bot.message_handler(commands=["palpites"])
def iniciar_palpite(mensagem):
    uid = str(mensagem.from_user.id)
    nome = mensagem.from_user.first_name
    estado_resultado[uid] = {"nome": nome}
    msg = bot.send_message(mensagem.chat.id, "🔢 Seu palpite: quantos rounds a FURIA fará?")
    bot.register_next_step_handler(msg, receber_palpite_furia)

def receber_palpite_furia(mensagem):
    uid = str(mensagem.from_user.id)
    try:
        furia = int(mensagem.text.strip())
        estado_resultado[uid]["furia"] = furia
        msg = bot.send_message(mensagem.chat.id, f"🔢 Quantos rounds o {adversario_nome} fará?")
        bot.register_next_step_handler(msg, receber_palpite_oponente)
    except:
        bot.reply_to(mensagem, "❌ Envie um número válido.")

def receber_palpite_oponente(mensagem):
    uid = str(mensagem.from_user.id)
    try:
        oponente = int(mensagem.text.strip())
        nome = estado_resultado[uid]["nome"]

        palpite = {
            "nome": nome,
            "palpite": {
                "furia": estado_resultado[uid]["furia"],
                "oponente": oponente,
                "adversario": adversario_nome
            }
        }

        palpites = carregar_json("palpites.json")
        palpites[uid] = palpite
        salvar_json("palpites.json", palpites)

        estado_resultado.pop(uid, None)
        bot.reply_to(mensagem, "✅ Palpite registrado com sucesso!")

    except:
        bot.reply_to(mensagem, "❌ Envie um número válido.")

# --- /verificar_resultado ---
@bot.message_handler(commands=["verificar_resultado"])
def verificar_resultado(mensagem):
    resultado_real = carregar_resultado()
    if not resultado_real:
        bot.reply_to(mensagem, "⚠️ O resultado real ainda não foi definido.")
        return

    palpites = carregar_json("palpites.json")
    pontuacao = carregar_json("pontuacao.json")
    acertos = []

    for uid, p in palpites.items():
        if p["palpite"] == resultado_real:
            nome = p["nome"]
            acertos.append(nome)
            if uid not in pontuacao:
                pontuacao[uid] = {"nome": nome, "pontos": 0}
            pontuacao[uid]["pontos"] += 1

    salvar_json("pontuacao.json", pontuacao)
    # salvar_json("palpites.json", {})  # Descomente para limpar os palpites após verificar

    if acertos:
        texto = "🏆 Palpites certos!\n\n" + "\n".join([f"🎉 {nome}" for nome in acertos])
    else:
        texto = "😕 Ninguém acertou dessa vez."

    bot.reply_to(mensagem, texto)

# --- Menu e outros comandos ---
def menu():
    return (
        "Escolha uma opção:\n"
        "/elenco - Ver elenco do time de CS2\n"
        "/partidas - Próximas partidas\n"
        "/historico - Histórico de partidas\n"
        "/loja - Loja oficial FURIA\n"
        "/palpites - Enviar palpite\n"
        "/verificar_resultado - Verificar palpites corretos"
    )

@bot.message_handler(commands=["start", "menu"])
def iniciar(mensagem):
    bot.reply_to(mensagem, f"Bem-vindo ao bot oficial FURIA CS2! 🎯\n\n{menu()}")

@bot.message_handler(commands=["elenco"])
def elenco(mensagem):
    texto = dados['Elenco'].get("CS2", "Elenco não disponível.")
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=["partidas"])
def partidas(mensagem):
    texto = dados['ProxPartidas'].get("CS2", "Sem partidas agendadas.")
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=["historico"])
def historico(mensagem):
    texto = dados['Historico'].get("CS2", "Histórico indisponível.")
    bot.reply_to(mensagem, texto)

@bot.message_handler(commands=["loja"])
def loja(mensagem):
    bot.reply_to(mensagem, "🛒 Loja oficial FURIA: https://www.furia.gg/")

@bot.message_handler(func=lambda m: True)
def responder(mensagem):
    bot.reply_to(mensagem, f"Use o menu abaixo para explorar informações do time de CS2 🖤\n\n{menu()}")

# Inicia o bot
bot.polling(timeout=60, long_polling_timeout=60)
