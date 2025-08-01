#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envia un resumen diario al canal Telegram
– Lista de símbolos con señales encontradas (todas las estrategias)
– Si no hay, mensaje “sin señales válidas”
"""

import os, datetime, requests, pandas as pd, telegram

# ───────────── CONFIGURACIÓN ──────────────
TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOLS = [
    "SPY","QQQ","AAPL","META","AMZN","NFLX","TSLA","NVDA",
    "MRNA","BAC","TNA","GLD","SLV","USO","XOM","CVX"
]
TIMEZONE = "America/New_York"          # para hora NY

# ───────────── UTILIDADES ─────────────────
def yf_1d(sym: str) -> pd.DataFrame:
    """Devuelve data intradía (1 min) del día actual en NY."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
    url += "?interval=1m&range=1d"
    j   = requests.get(url, timeout=20).json()
    ts  = j["chart"]["result"][0]["timestamp"]
    q   = j["chart"]["result"][0]["indicators"]["quote"][0]
    df  = pd.DataFrame(q, index=pd.to_datetime(ts, unit="s", utc=True))
    return df.tz_convert(TIMEZONE)

# ───────────── ESTRATEGIAS (ejemplos) ─────
def e1(df):            # primera vela roja (PUT)
    s = df["close"].between(df["open"], df["open"]*0.999)
    return (df.index.hour == 10) & s

def e2(df):            # ruptura piso gap (PUT)
    gap_low = df["low"].iloc[0]
    return df["close"] < gap_low

def e3(df):            # modelo 4 pasos (PUT)
    ma40 = df["close"].rolling(40).mean()
    top  = ma40 + ma40*0.01
    return (df["high"] > top) & (df["close"] < top)

def e4(df):            # hangar diario (PUT)
    o,h,l,c = [df[x].iloc[-1] for x in ("open","high","low","close")]
    body, upper = abs(c-o), h-max(c,o)
    return (upper > 2*body) and (c < o)

STRATS = [
    (e1, "E1 roja apertura"),
    (e2, "E2 piso gap"),
    (e3, "E3 4 pasos"),
    (e4, "E4 hangar diario")
]

# ───────────── MAIN ───────────────────────
def to_bool(x):
    """Convierte cualquier tipo (Series/bool) a bool."""
    if isinstance(x, pd.Series):
        return bool(x.any())           # basta con 1 True
    return bool(x)

def main():
    hits, bot = [], telegram.Bot(TOKEN)

    for s in SYMBOLS:
        df = yf_1d(s)
        for f, name in STRATS:
            if to_bool(f(df)):
                hits.append(f"• {s}  {name}")

    today = datetime.date.today().strftime("%Y-%m-%d")
    if hits:
        msg = "📋 *Resumen diario* " + today + "\n" + "\n".join(hits)
    else:
        msg = f"📋 *{today}* – sin señales válidas hoy"

    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

if __name__ == "__main__":
    main()
