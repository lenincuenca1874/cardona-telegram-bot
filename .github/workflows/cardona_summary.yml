import os, datetime as dt, json
from telegram import Bot

TOKEN = os.environ['TELEGRAM_TOKEN'].strip()
CHAT  = os.environ['TELEGRAM_CHAT_ID'].strip()
bot   = Bot(token=TOKEN)

# El workflow almacena hits del día en un artefacto JSON sencillo.
LOGFILE = "signals_today.json"

def load_hits():
    if os.path.exists(LOGFILE):
        with open(LOGFILE,'r') as f:
            return json.load(f)
    return []

def clear_hits():
    if os.path.exists(LOGFILE):
        os.remove(LOGFILE)

def main():
    hits = load_hits()
    today = dt.datetime.now().astimezone(
        dt.timezone(dt.timedelta(hours=-4))).strftime('%Y-%m-%d')
    if hits:
        text = f"*Resumen Cardona {today}*\n\n"
        for h in hits:
            text += f"• {h['time']} NY – {h['tkr']} – {h['strat']}\n"
    else:
        text = f"*Resumen Cardona {today}*\n\nSin señales hoy."

    bot.send_message(CHAT, text, parse_mode='Markdown')
    clear_hits()

if __name__ == "__main__":
    main()
