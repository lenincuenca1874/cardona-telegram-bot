from utils import send_to_telegram
from datetime import datetime

def run_bot():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"✅ *SPY* activó *Primera vela roja apertura*

🕒 {now}

📊 Análisis técnico automático:

- RSI: 34
- Precio tocando EMA200
- Patrón: Velón de reversión

🎯 Entrada sugerida: $435.20
📉 Stop Loss: $433.80
📈 Take Profit: $439.80"
    send_to_telegram(msg)

if __name__ == "__main__":
    run_bot()
