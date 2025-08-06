import os, json, datetime
from telegram import Bot

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
bot = Bot(token=TOKEN)

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    resumen = f"📊 *Resumen del día - {now}*"


"
    if not os.path.exists("signals_today.json"):
        resumen += "No se generaron señales hoy."
    else:
        with open("signals_today.json", "r") as f:
            hits = json.load(f)
        if not hits:
            resumen += "No se generaron señales hoy."
        else:
            for h in hits:
                resumen += f"✅ *{h['tkr']}* → {h['strat']} 🕒 {h['time']}
"

    bot.send_message(chat_id=CHAT_ID, text=resumen, parse_mode="Markdown")

if __name__ == "__main__":
    main()
