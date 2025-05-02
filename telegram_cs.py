import telebot
import json

# Chave da API do Telegram
chave_api = "8163572933:AAH5r4Ip8ZBVuBOlaqFEH18s-EwzOZ7AxNA"
bot = telebot.TeleBot(chave_api)


estado_resultado = {}

ADMIN_ID = "7455803576"
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


#Função para saber o ID
@bot.message_handler(commands=["meuid"])
def meu_id(mensagem):
    bot.reply_to(mensagem, f"🆔 Seu ID é: {mensagem.from_user.id}")

def carregar_adversario():
    dados = carregar_json("adversario.json")
    return dados.get("nome,", "")

adversario_nome = carregar_adversario()

def salvar_adversario(nome):
    salvar_json("adversario.json", {"nome": nome})


@bot.message_handler(commands=["setar_adversario"])
def setar_adversario(mensagem):
    if str(mensagem.from_user.id) != ADMIN_ID:
        bot.reply_to(mensagem, "🚫 Você não tem permissão para usar este comando.")
        return

    partes = mensagem.text.strip().split(maxsplit=1)
    if len(partes) != 2:
        bot.reply_to(mensagem, "❗ Use: /setar_adversario <nome_do_adversário>")
        return

    novo_adversario = partes[1]
    salvar_adversario(novo_adversario)

    # Atualiza a variável global
    global adversario_nome
    adversario_nome = novo_adversario

    bot.reply_to(mensagem, f"✅ Adversário atualizado para: {adversario_nome}")

# --- /palpites ---

def carregar_status_palpites():
    dados = carregar_json("status_palpites.json")
    return dados.get("ativo", False) #Padrão palpites fechados

def salvar_status_palpites(ativo: bool):
    salvar_json("status_palpites.json", {"ativo": ativo})

palpites_ativos = carregar_status_palpites()

@bot.message_handler(commands=["palpites"])
def iniciar_palpite(mensagem):
    global palpites_ativos
    if not palpites_ativos:
        bot.reply_to(mensagem, "❌ Os palpites estão encerrados no momento.")
        return

    uid = str(mensagem.from_user.id)
    nome = mensagem.from_user.first_name
    estado_resultado[uid] = {"nome": nome}
    msg = bot.send_message(mensagem.chat.id, "🔢 Seu palpite: quantos rounds a FURIA fará?")
    bot.register_next_step_handler(msg, receber_palpite_furia)

@bot.message_handler(commands=["encerrar_palpites"])
def encerrar_palpites(mensagem):
    if str(mensagem.from_user.id) != ADMIN_ID:
        bot.reply_to(mensagem, "🚫 Você não tem permissão.")
        return
    salvar_status_palpites(False)
    global palpites_ativos
    palpites_ativos = False
    bot.reply_to(mensagem, "🔒 Palpites encerrados.")

@bot.message_handler(commands=["abrir_palpites"])
def abrir_palpites(mensagem):
    if str(mensagem.from_user.id) != ADMIN_ID:
        bot.reply_to(mensagem, "🚫 Você não tem permissão.")
        return
    salvar_status_palpites(True)
    global palpites_ativos
    palpites_ativos = True
    bot.reply_to(mensagem, "🔓 Palpites abertos.")

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

    # Resultado real
    resultado_texto = f"🔴 Resultado final:\nFURIA: {resultado_real['furia']} x {resultado_real['oponente']} {resultado_real['adversario']}"

    for uid, p in palpites.items():
        if p["palpite"]["furia"] == resultado_real["furia"] and p["palpite"]["oponente"] == resultado_real["oponente"]:
            nome = p["nome"]
            acertos.append((uid, nome))

            if uid not in pontuacao:
                pontuacao[uid] = {"nome": nome, "pontos": 0}
            pontuacao[uid]["pontos"] += 1

    salvar_json("pontuacao.json", pontuacao)

    # Notifica individualmente
    for uid, nome in acertos:
        try:
            bot.send_message(uid, f"🏆 Parabéns, {nome}! Você acertou o palpite da partida! 🎉\n{resultado_texto}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {nome} ({uid}): {e}")

    if acertos:
        texto = f"✅ Resultado verificado. {len(acertos)} usuário(s) acertaram!\n{resultado_texto}"
    else:
        texto = f"😕 Ninguém acertou dessa vez.\n{resultado_texto}"

    bot.reply_to(mensagem, texto)

    # (Opcional) Limpar os palpites depois da verificação
    # salvar_json("palpites.json", {})


#Função para definir resultados 
@bot.message_handler(commands=["definir_resultado"])
def definir_resultado(mensagem):
    if str(mensagem.from_user.id) != ADMIN_ID:
        bot.reply_to(mensagem, "🚫 Você não tem permissão para usar este comando.")
        return

    try:
        partes = mensagem.text.strip().split()
        if len(partes) != 3:
            bot.reply_to(mensagem, "❗ Formato incorreto. Use: /definir_resultado <FURIA> <Adversário>")
            return

        furia = int(partes[1])
        oponente = int(partes[2])

        resultado = {
            "furia": furia,
            "oponente": oponente,
            "adversario": adversario_nome
        }

        salvar_json("resultado_real.json", resultado)

        # Executa a verificação automaticamente
        verificar_resultado(mensagem)  # Reaproveita a função que já existe

    except Exception as e:
        print(e)
        bot.reply_to(mensagem, "❌ Ocorreu um erro ao definir o resultado.")

# --- Menu e outros comandos ---
def menu():
    return (
        "Escolha uma opção:\n"
        "/elenco - Ver elenco do time de CS2\n"
        "/partidas - Próximas partidas\n"
        "/historico - Histórico de partidas\n"
        "/loja - Loja oficial FURIA\n"
        "/palpites - Enviar palpite\n"
        "/top10 - TOP 10 dos maiores pontuadores da comunidade"
    )

@bot.message_handler(commands=["top10"])
def maiores_pontuadores(mensagem):
    # Carrega os dados de pontuação
    pontuacao = carregar_json("pontuacao.json")

    # Ordena os usuários pela pontuação em ordem decrescente
    pontuadores_ordenados = sorted(pontuacao.items(), key=lambda x: x[1]["pontos"], reverse=True)

    # Cria uma mensagem com os 10 maiores pontuadores
    texto = "🏆 **Top 10 Maiores Pontuadores**:\n"
    for i, (uid, dados) in enumerate(pontuadores_ordenados[:10], 1):
        nome = dados["nome"]
        pontos = dados["pontos"]
        texto += f"{i}. {nome} - {pontos} pontos\n"

    if not pontuadores_ordenados:
        texto = "❌ Não há pontuações registradas ainda."

    # Envia a lista de pontuadores
    bot.reply_to(mensagem, texto)


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

# Necessario atualizar o resultado da partida depois que acaba, e notificar os usuarios

# /abrir_palpites
# /encerrar_palpites
# /setar_adversario
# /setar_adversario
# /definir_resultado