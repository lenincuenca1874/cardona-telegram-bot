import os, json
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from telegram import Bot

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
TIMEZONE = "America/New_York"

SYMBOLS = [
    "SPY", "QQQ", "AAPL", "META", "AMZN", "NFLX", "TSLA", "NVDA",
    "MRNA", "BAC", "TNA", "GLD", "SLV", "USO", "XOM", "CVX"
]

bot = Bot(token=TOKEN)

def get_price_data(symbol):
    return yf.download(symbol, period="7d", interval="5m", progress=False)

def plot_chart(df, symbol):
    fig, ax = plt.subplots()
    df["Close"].tail(60).plot(ax=ax, title=f"{symbol} Últimos 60 minutos")
    img_path = f"chart_{symbol}.png"
    fig.savefig(img_path)
    plt.close(fig)
    return img_path

def send_signal(tkr, strat, df):
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"✅ *{tkr}* activó *{strat}*"

Hora: {now}
Análisis técnico automático:"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

    chart = plot_chart(df, tkr)
    with open(chart, "rb") as img:
        bot.send_photo(chat_id=CHAT_ID, photo=img)
    os.remove(chart)

    save_hit({"tkr": tkr, "strat": strat, "time": now})

def save_hit(hit):
    if os.path.exists("signals_today.json"):
        with open("signals_today.json", "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(hit)
    with open("signals_today.json", "w") as f:
        json.dump(data, f, indent=2)

def detect_strategy_1(df):
    return False

def detect_strategy_2(df):
    return False

def detect_strategy_3(df):
    return False

def detect_strategy_4(df):
    return False

def main():
    for tkr in SYMBOLS:
        df = get_price_data(tkr)
        if df.empty: continue

        if detect_strategy_1(df):
            send_signal(tkr, "Estrategia 1 - 1ra Vela Roja", df)
        if detect_strategy_2(df):
            send_signal(tkr, "Estrategia 2 - Ruptura del GAP", df)
        if detect_strategy_3(df):
            send_signal(tkr, "Estrategia 3 - Canal Bajista", df)
        if detect_strategy_4(df):
            send_signal(tkr, "Estrategia 4 - Hangar Diario", df)

if __name__ == "__main__":
    main()
