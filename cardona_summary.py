import os
from datetime import datetime
import json

def enviar_resumen():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    resumen = f"📊 *Resumen del día - {now}*"

    try:
        with open("signals_today.json", "r") as f:
            signals = json.load(f)
    except FileNotFoundError:
        signals = []

    if not signals:
        resumen += "\n\nNo se encontraron señales válidas hoy."
    else:
        for signal in signals:
            resumen += f"\n\n🟢 *{signal['tkr']}* - Estrategia: *{signal['strat']}* a las {signal['time']}"

    send_to_telegram(resumen)

def send_to_telegram(msg):
    import requests
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload)

if __name__ == "__main__":
    enviar_resumen()
