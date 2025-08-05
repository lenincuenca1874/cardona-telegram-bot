import os
from datetime import datetime
import json

def send_signal(tkr, strat):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"✅ *{tkr}* activó *{strat}* a las {ts}"
    print(msg)  # En producción, esto se envía a Telegram
    save_hit({"tkr": tkr, "strat": strat, "time": ts})

def save_hit(hit):
    path = "signals_today.json"
    data = []
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    data.append(hit)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Ejemplo de llamada
send_signal("AAPL", "Promedio 40 Reversión")
