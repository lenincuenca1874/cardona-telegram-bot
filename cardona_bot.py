#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Escaneo intradía (cada 5 min) y alerta a Telegram cuando se cumple
cualquiera de las 4 estrategias básicas.
"""

import os, datetime as dt, requests, pandas as pd, yfinance as yf
from zoneinfo import ZoneInfo

TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOLS = [
    "SPY","QQQ","AAPL","META","AMZN","NFLX","TSLA","NVDA",
    "MRNA","BAC","TNA","GLD","SLV","USO","XOM","CVX"
]

TZ = ZoneInfo("America/New_York")           # hora oficial NY ─┐
MKT_OPEN  = dt.time(9, 30)                  #                  ├─ límites
MKT_CLOSE = dt.time(16, 0)                  # ─────────────────┘


# ────────────── utilidades ──────────────
def yf_1m(ticker: str) -> pd.DataFrame:
    return yf.download(ticker, period="1d", interval="1m", progress=False)

def to_bool(obj) -> bool:
    """
    Toma la salida booleana de una estrategia (Series o DataFrame)
    y devuelve un bool nativo sin ambigüedad.
    """
    if isinstance(obj, pd.DataFrame):
        return obj.iloc[-1].any()           # True si *alguna* col. es True
    return bool(obj.iloc[-1])

def send(msg: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID,
                             "text": msg,
                             "parse_mode": "Markdown"},
                  timeout=10)

# ─────────── estrategias intradía ───────────
def sma(s, n): return s.rolling(n).mean()

def e1(d):                             # EMA9 ↗ cruza EMA20
    e9, e20 = d.Close.ewm(span=9).mean(), d.Close.ewm(span=20).mean()
    return (e9 > e20) & (e9.shift() <= e20.shift())

def e2(d):                             # Ruptura ORH + volumen ↑
    orh = d.between_time("09:30", "10:30").High.max()
    return (d.Close > orh) & (d.Volume > d.Volume.rolling(20).mean())

def e3(d):                             # EMA9 ↘ cruza EMA20
    e9, e20 = d.Close.ewm(span=9).mean(), d.Close.ewm(span=20).mean()
    return (e9 < e20) & (e9.shift() >= e20.shift())

def e4(d):                             # Ruptura ORB- (mínimo)
    orb = d.between_time("09:30", "10:30").Low.min()
    return (d.Close < orb) & (d.Volume > d.Volume.rolling(20).mean())

STRATS = {"E1 (long)": e1, "E2 (ORH)": e2,
          "E3 (short)": e3, "E4 (ORB-)": e4}

# ─────────── main loop ───────────
def main():
    now = dt.datetime.now(TZ).time()
    if not (MKT_OPEN <= now < MKT_CLOSE):
        return

    hits = []
    for sym in SYMBOLS:
        df = yf_1m(sym)
        if df.empty:
            continue
        for tag, fn in STRATS.items():
            if to_bool(fn(df)):
                hits.append(f"*{sym}*  → {tag}")
                break

    if hits:
        send("🚨 *Señales intradía*\n" + "\n".join(hits))

if __name__ == "__main__":
    main()
