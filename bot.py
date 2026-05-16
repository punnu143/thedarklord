import telebot
import requests
import json
import os
import random
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ================= FILES =================
MEMORY_FILE = "memory.json"
BANNED_FILE = "banned.json"
USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"

SECRET_KEY = "dark@123"  # 🔐 change this

# ================= LOAD =================
def load_file(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

memory = load_file(MEMORY_FILE, {})
banned_users = load_file(BANNED_FILE, [])
all_users = load_file(USERS_FILE, [])
admins = load_file(ADMINS_FILE, [])

# FIRST ADMIN (IMPORTANT)
if not admins:
    print("⚠️ No admin found. Add your Telegram ID in admins.json")

# ================= STATES =================
bot_active = True
mode = "dark"

# ================= ADMIN CHECK =================
def is_admin(user_id):
    return user_id in admins

# ================= AI =================
def ask_ai(user_id, text):

    uid = str(user_id)

    if uid not in memory:
        memory[uid] = []

    memory[uid].append({"role": "user", "content": text})

    if mode == "romantic":
        system_prompt = "You are a romantic caring human, Hinglish."
    elif mode == "normal":
        system_prompt = "You are a friendly human."
    else:
        system_prompt = "You are Dark Lord, savage, human-like, Hinglish."

    messages = [{"role": "system", "content": system_prompt}] + memory[uid][-10:]

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": messages,
                "temperature": 0.9
            },
            timeout=10
        )

        if r.status_code != 200:
            return random.choice([
                "Network issue...",
                "Signal lost...",
                "Try again later..."
            ])

        data = r.json()

        if "choices" not in data:
            return "AI error..."

        reply = data["choices"][0]["message"]["content"]

        memory[uid].append({"role": "assistant", "content": reply})
        save(MEMORY_FILE, memory)

        return reply

    except Exception as e:
        print("ERROR:", e)
        return random.choice([
            "Hmm...",
            "Not now...",
            "Later..."
        ])

# ================= ADMIN COMMANDS =================

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"Your ID: {message.from_user.id}")

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if not is_admin(message.from_user.id):
        return

    try:
        parts = message.text.split()
        uid = int(parts[1])
        key = parts[2]

        if key != SECRET_KEY:
            bot.reply_to(message, "Wrong key")
            return

        if uid not in admins:
            admins.append(uid)
            save(ADMINS_FILE, admins)
            bot.reply_to(message, "Admin added 👑")
        else:
            bot.reply_to(message, "Already admin")

    except:
        bot.reply_to(message, "Usage: /addadmin user_id key")

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if not is_admin(message.from_user.id):
        return

    try:
        uid = int(message.text.split()[1])
        admins.remove(uid)
        save(ADMINS_FILE, admins)
        bot.reply_to(message, "Admin removed")
    except:
        bot.reply_to(message, "Error")

@bot.message_handler(commands=['admins'])
def list_admins(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, str(admins))

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id):
        return

    try:
        uid = int(message.text.split()[1])
        if uid not in banned_users:
            banned_users.append(uid)
            save(BANNED_FILE, banned_users)
        bot.reply_to(message, "User banned")
    except:
        bot.reply_to(message, "Usage: /ban user_id")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id):
        return

    try:
        uid = int(message.text.split()[1])
        if uid in banned_users:
            banned_users.remove(uid)
            save(BANNED_FILE, banned_users)
        bot.reply_to(message, "User unbanned")
    except:
        bot.reply_to(message, "Error")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if not is_admin(message.from_user.id):
        return

    msg = message.text.replace("/broadcast ", "")

    for u in all_users:
        try:
            bot.send_message(u, msg)
        except:
            pass

    bot.reply_to(message, "Broadcast done")

@bot.message_handler(commands=['mode'])
def mode_change(message):
    global mode

    if not is_admin(message.from_user.id):
        return

    try:
        mode = message.text.split()[1]
        bot.reply_to(message, f"Mode: {mode}")
    except:
        bot.reply_to(message, "Use /mode dark|romantic|normal")

@bot.message_handler(commands=['users'])
def users(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, f"Users: {len(all_users)}")

@bot.message_handler(commands=['off'])
def off(message):
    global bot_active
    if is_admin(message.from_user.id):
        bot_active = False
        bot.reply_to(message, "Bot OFF")

@bot.message_handler(commands=['on'])
def on(message):
    global bot_active
    if is_admin(message.from_user.id):
        bot_active = True
        bot.reply_to(message, "Bot ON")

# ================= MAIN =================

@bot.message_handler(func=lambda m: True)
def main(message):

    user_id = message.from_user.id

    if user_id not in all_users:
        all_users.append(user_id)
        save(USERS_FILE, all_users)

    if user_id in banned_users:
        return

    if not bot_active:
        return

    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(random.uniform(1, 2))

    reply = ask_ai(user_id, message.text)

    bot.reply_to(message, reply)

# ================= RUN =================

print("🔥 Dark Lord Fully Loaded...")

while True:
    try:
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=30
        )
    except Exception as e:
        print("Polling Error:", e)
        time.sleep(5)
