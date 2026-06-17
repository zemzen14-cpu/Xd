import telebot
from flask import Flask, request
from gtts import gTTS
import os
import tempfile

TOKEN = "8614415117:AAFigLbkXXEaos43DoDS2oyKqK5311fGWks"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# -----------------------------
# COMANDOS DEL BOT
# -----------------------------

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 Bot activo y resonando entre luz y sombra, Cristopher.")

@bot.message_handler(commands=['voz'])
def voz(message):
    texto = message.text.replace("/voz", "").strip()

    if texto == "":
        bot.reply_to(message, "🎙️ Usa /voz seguido del texto.\nEjemplo:\n/voz Hola Cristopher")
        return

    # Mensaje previo angelical oscuro
    bot.reply_to(message, "🌑✨ Transformando tu voz en oscuridad…")

    # Crear audio temporal
    tts = gTTS(text=texto, lang="es")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp.name)

    # Enviar audio
    with open(temp.name, "rb") as audio:
        bot.send_audio(message.chat.id, audio)

    # Borrar archivo temporal
    os.remove(temp.name)

# -----------------------------
# SIN ECO — NO RESPONDE A MENSAJES NORMALES
# -----------------------------

# (No hay handler para mensajes normales)

# -----------------------------
# WEBHOOK PARA RENDER
# -----------------------------

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://xd-2-ybyd.onrender.com/" + TOKEN)
    return "Webhook set", 200

# -----------------------------
# INICIO DEL SERVIDOR
# -----------------------------

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
