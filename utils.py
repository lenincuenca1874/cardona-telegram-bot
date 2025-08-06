import os
import requests

TOKEN = os.getenv("8065055495:AAEhZ1X39y6M92-VzIqi4f2rkDlbH3SYWRE")
CHAT_ID = os.getenv("7894610336")

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN o CHAT_ID no configurados")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()
