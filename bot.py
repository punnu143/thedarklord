import telebot
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("TOKEN:", TELEGRAM_TOKEN)
print("API KEY:", GROQ_API_KEY)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_ai(text):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Reply like a real human in Hinglish."},
                    {"role": "user", "content": text}
                ]
            },
            timeout=10
        )

        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text)

        if r.status_code != 200:
            return "Server busy..."

        data = r.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("ERROR:", e)
        return "Connection error..."

@bot.message_handler(func=lambda m: True)
def main(message):
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)

    reply = ask_ai(message.text)

    bot.reply_to(message, reply)

print("🔥 Bot Running...")

bot.infinity_polling()
