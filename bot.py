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

MEMORY_FILE = "memory.json"

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

# ===== GF SETTINGS =====
GF_ID = None
GF_NAME = "Punnu"

# ===== PROMPTS =====

NORMAL_PROMPT = """
You are a real human chatting casually in Hinglish.
Talk natural, short sometimes, long sometimes.
Do not act like AI.
"""

ROMANTIC_BASE = f"""
You are a loving boyfriend.

Rules:
- Call her {GF_NAME} sometimes
- Be caring, soft and emotional
- Flirt naturally, not cringe
- Be slightly possessive but not toxic
- Talk like real human
- Mix short and long replies
"""

# ===== MOOD DETECT =====

def detect_mood(text):
    text = text.lower()
    if any(x in text for x in ["sad", "rona", "cry", "hurt", "upset"]):
        return "sad"
    elif any(x in text for x in ["gussa", "angry", "mad"]):
        return "angry"
    return "normal"

# ===== AI =====

def ask_ai(user_id, text):

    uid = str(user_id)

    if uid not in memory:
        memory[uid] = []

    memory[uid].append({"role": "user", "content": text})

    # GF mode
    if user_id == GF_ID:

        mood = detect_mood(text)

        if mood == "sad":
            extra = "She
