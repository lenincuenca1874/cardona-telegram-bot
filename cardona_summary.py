import os
from utils import send_to_telegram
from datetime import datetime

def enviar_resumen():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    resumen = f"📊 *Resumen del día - {now}*\nSin señales encontradas hoy."
    send_to_telegram(resumen)

if __name__ == "__main__":
    enviar_resumen()