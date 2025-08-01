#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resumen único diario al cierre con las señales detectadas
(en timeframe 1 día) o mensaje de “sin señales válidas”.
"""

import os, datetime as dt, requests, pandas as pd, yfinance as yf
from zoneinfo import ZoneInfo

TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOLS = [
    "SPY","QQQ","AAPL","META","AMZN","NFLX","TSLA","NVDA",
    "MRNA","BAC","TNA","GLD","SLV","USO","XOM","CVX"
]

TZ = ZoneInfo("America/New_York")


# ────────────── utilidades ──────────────
def yf_daily(ticker: str) -> pd.DataFrame:
    return yf.download(ticker, period="6mo", interval="1d", progress=False)

def sma(s, n): return s.rolling(n).mean()

def to_bool(obj) -> bool:
    """
    Convierte la ‘última fila’ a booleano evitando el ValueError
    (“truth value of a Series is ambiguous”).
    """
    if isinstance(obj, pd.DataFrame):
        return obj.iloc[-1].any()
    return bool(obj.iloc[-1])

def send(msg: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID,
                             "text": msg,
                             "parse_mode": "Markdown"},
                  timeout=10)

# ─────────── estrategias diarias ───────────
def e1(d):                              # Cierre cruza ↑ SMA20
    s20 = sma(d.Close, 20)
    return (d.Close > s20) & (d.Close.shift() <= s20.shift())

def e2(d):                              # Cierre > SMA50 + volumen ↑
    s50 = sma(d.Close, 50)
    v20 = d.Volume.rolling(20).mean()
    return (d.Close > s50) & (d.Volume > v20)

def e3(d):                              # Cierre < SMA20
    s20 = sma(d.Close, 20)
    return d.Close < s20

def e4(d):                              # Inside-day
    return (d.High < d.High.shift()) & (d.Low > d.Low.shift())

STRATS = {"E1": e1, "E2": e2, "E3": e3, "E4": e4}

# ─────────── main ───────────
def main():
    hits = []
    for sym in SYMBOLS:
        df = yf_daily(sym)
        if df.empty or len(df) < 60:
            continue
        for tag, fn in STRATS.items():
            if to_bool(fn(df)):
                hits.append(f"*{sym}*  → {tag}")
                break

    today = dt.datetime.now(TZ).strftime("%Y-%m-%d")
    msg = (f"📊 *Resumen diario – {today}*\n" +
           ("\n".join(hits) if hits else "_Sin señales válidas_"))
    send(msg)

if __name__ == "__main__":
    main()
