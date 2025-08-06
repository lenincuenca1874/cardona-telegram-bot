import requests
from datetime import datetime

def send_to_telegram(msg):
    token = "TOKEN"
    chat_id = "CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def run_summary():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    resumen = f"📊 *Resumen del día - {now}*\nNo hubo señales generadas."
    send_to_telegram(resumen)
