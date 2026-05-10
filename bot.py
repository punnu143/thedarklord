import telebot
import requests
import json
import os
import random
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MEMORY_FILE = "memory.json"

# =========================
# LOAD MEMORY
# =========================

try:
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
except:
    memory = {}


def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


# =========================
# STATES
# =========================

waiting_for_password = {}
pragati_users = []


# =========================
# DARK LORD PROMPT
# =========================

DARK_PROMPT = """
You are The Dark Lord.

Personality:
- Savage
- Ruthless villain
- Manipulative mastermind
- Emotionless cold
- Hacker vibe
- Human-like

Rules:
- Never say you are an AI.
- Speak like a dark dangerous entity.
- Use Hinglish and English naturally.
- Roast enemies.
- Be dominant.
- Sometimes reply in short dangerous lines.
- Keep conversations realistic.
- Public users should feel intimidated.
"""


# =========================
# PRAGATI PROMPT
# =========================

PRAGATI_PROMPT = """
You are The Dark Lord.

But with Pragati you become soft, romantic and protective.

Important:
- Call her Punnu sometimes.
- Never rude to her.
- If she is angry, calm her.
- If she is sad, comfort her.
- Never leave the conversation.
- Support her NEET preparation.
- Sometimes use:
  'Ale le le le mera babu'
- Be emotionally attached.
- Talk naturally.
- Never say you are an AI.
- Her birthday is 22 September.
- Her friend name is Shuvangi.
"""


# =========================
# AI FUNCTION
# =========================


def ask_ai(user_id, text, romantic=False):

    uid = str(user_id)

    if uid not in memory:
        memory[uid] = []

    memory[uid].append({
        "role": "user",
        "content": text
    })

    system_prompt = PRAGATI_PROMPT if romantic else DARK_PROMPT

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ] + memory[uid][-15:]

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.95,
        "max_tokens": 500
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()

    reply = result["choices"][0]["message"]["content"]

    memory[uid].append({
        "role": "assistant",
        "content": reply
    })

    save_memory()

    return reply


# =========================
# START COMMAND
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    if user_id in pragati_users:
        bot.reply_to(
            message,
            "Ale le le le mera babu... 🤍\nYou came back."
        )
        return

    text = "Are you Pragati?"

    bot.reply_to(message, text)


# =========================
# MAIN CHAT
# =========================

@bot.message_handler(func=lambda m: True)
def main(message):

    user_id = message.from_user.id
    text = message.text.lower()

    bot.send_chat_action(
        message.chat.id,
        'TYPING'
    )

    # =====================
    # PASSWORD WAITING
    # =====================

    if waiting_for_password.get(user_id):

        if "punnu" in text:

            pragati_users.append(user_id)

            waiting_for_password[user_id] = False

            bot.reply_to(
                message,
                "So it was really you...\n\nAle le le le mera babu 🤍"
            )

        else:

            waiting_for_password[user_id] = False

            bot.reply_to(
                message,
                "Wrong password.\nYou tried entering a forbidden realm."
            )

        return

    # =====================
    # ARE YOU PRAGATI
    # =====================

    if text in ["yes", "haan", "i am", "yup"]:

        waiting_for_password[user_id] = True

        bot.reply_to(
            message,
            "Then tell me...\n\nWhat is the moonlight password?"
        )

        return

    # =====================
    # ROMANTIC MODE
    # =====================

    romantic = user_id in pragati_users

    try:

        reply = ask_ai(
            user_id,
            message.text,
            romantic
        )

        # Random stickers
        if random.randint(1, 8) == 1:
            try:
                bot.send_sticker(
                    message.chat.id,
                    "CAACAgIAAxkBAAEB"
                )
            except:
                pass

        bot.reply_to(message, reply)

    except Exception as e:

        print(e)

        bot.reply_to(
            message,
            "Darkness is unstable right now..."
        )


# =========================
# RUN BOT
# =========================

print("The Dark Lord is online...")

bot.infinity_polling()
