# 🤖 Instagram Cookie Checker Telegram Bot

A powerful and secure Telegram bot that checks the validity of Instagram cookies in bulk. Built for automation, moderation, and ease of use.

## 🔧 Features

- ✅ Bulk cookie checking from `.txt` files
- 🔍 Account info extraction (username, email, verification status)
- 📂 Returns `valid.txt` with working cookies
- 🕵️ CAPTCHA / checkpoint detection
- 🌐 Proxy rotation support (`proxies.txt`)
- 📦 JSON & string cookie format support
- 🔑 Secure access with redeem code system
- 🛡️ Admin tools: `/ban`, `/unban`, `/broadcast`
- 📈 Logging and file-based stats
- 💬 User-friendly via Telegram chat

## 🚀 Usage

1. Start the bot using `/start`
2. Redeem access with `/redeem <your_code>`
3. Upload a `.txt` file containing one cookie per line
4. The bot checks each cookie and sends back `valid.txt`

Example cookie formats:
- `ds_user_id=123; sessionid=abc...; csrftoken=xyz;`
- JSON cookie: `[{"name": "sessionid", "value": "abc", ...}]`

## ⚙️ Installation

```bash
git clone https://github.com/DhautarChor/ig-cookie-checker-bot.git
cd ig-cookie-checker-bot
pip install -r requirements.txt
python bot.py
