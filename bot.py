import os
import telebot
import requests
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS

TOKEN = os.getenv("8614415117:AAFigLbkXXEaos43DoDS2oyKqK5311fGWks")
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# ============================
#   COMANDO /info
# ============================

@bot.message_handler(commands=['info'])
def info_user(message):
    try:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Uso: /info @usuario")
            return

        username = message.text.split()[1].replace("@", "")
        url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id=@{username}"

        r = requests.get(url).json()

        if not r.get("ok"):
            bot.reply_to(message, "No pude obtener información. ¿El usuario existe?")
            return

        data = r["result"]

        name = data.get("first_name", "Desconocido")
        last = data.get("last_name", "")
        bio = data.get("bio", "Sin bio")

        text = f"""
🔍 *Inspector de Usuarios*
👤 *Usuario:* @{username}
📛 *Nombre:* {name} {last}
📜 *Bio:* {bio}
        """

        # Enviar foto primero
        with open("pikachu.png", "rb") as foto:
            bot.send_photo(message.chat.id, foto)

        # Botones Ban / Unban
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🚫 Banear", callback_data=f"ban:{username}"),
            InlineKeyboardButton("✅ Desbanear", callback_data=f"unban:{username}")
        )

        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


# ============================
#   BOTONES BAN / UNBAN
# ============================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        action, username = call.data.split(":")
        chat_id = call.message.chat.id

        info = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id=@{username}"
        ).json()

        if not info.get("ok"):
            bot.answer_callback_query(call.id, "No pude obtener al usuario.")
            return

        user_id = info["result"]["id"]

        if action == "ban":
            bot.ban_chat_member(chat_id, user_id)
            bot.answer_callback_query(call.id, f"Usuario @{username} baneado.")

        elif action == "unban":
            bot.unban_chat_member(chat_id, user_id)
            bot.answer_callback_query(call.id, f"Usuario @{username} desbaneado.")

    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}")


# ============================
#   COMANDO /voz (gTTS)
# ============================

@bot.message_handler(commands=['voz'])
def voz(message):
    try:
        texto = message.text.replace("/voz", "").strip()

        if texto == "":
            bot.reply_to(message, "Uso: /voz <texto>")
            return

        # Crear audio temporal
        tts = gTTS(text=texto, lang="es")
        filename = "voz_temp.mp3"
        tts.save(filename)

        # Enviar audio
        with open(filename, "rb") as audio:
            bot.send_audio(message.chat.id, audio)

        # Borrar archivo temporal
        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


# ============================
#   WEBHOOK PARA RENDER
# ============================

@server.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@server.route("/")
def index():
    return "Bot funcionando en Render", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.getenv('RENDER_URL')}/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
