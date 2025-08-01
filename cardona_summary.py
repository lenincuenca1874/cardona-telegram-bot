#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envia UN resumen diario al canal de Telegram:
• Lista de símbolos con señales encontradas (todas las estrategias)
• Si no hay ninguna → mensaje “sin señales válidas”
"""

import os, datetime as dt, requests, pandas as pd, yfinance as yf
from zoneinfo import ZoneInfo

# ───────────────────────── CONFIGURACIÓN ──────────────────────────
TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOLS = [
    "SPY","QQQ","AAPL","META","AMZN","NFLX","TSLA","NVDA",
    "MRNA","BAC","TNA","GLD","SLV","USO","XOM","CVX"
]

TIMEZONE = ZoneInfo("America/New_York")     # para estampar la hora en NY

# ────────────────────────── UTILIDADES ────────────────────────────
def yf_d(sym: str) -> pd.DataFrame:
    """Descarga los últimos 60 días en daily (para SMA, etc.)."""
    return yf.download(sym, period="3mo", interval="1d", progress=False)

def sma(series: pd.Series, n: int = 20):
    return series.rolling(n).mean()

def to_bool(serie: pd.Series) -> bool:
    return bool(serie.iloc[-1])

def send(msg: str) -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)

# ────────────────────────── ESTRATEGIAS (DIARIAS) ─────────────────
def e1(df):  # Cierre > SMA20 y el día anterior ≤ SMA20
    sma20 = sma(df.Close, 20)
    return (df.Close > sma20) & (df.Close.shift() <= sma20.shift())

def e2(df):  # Cierre > SMA50 y volumen > vol. medio 20d
    sma50 = sma(df.Close, 50)
    vmean = df.Volume.rolling(20).mean()
    return (df.Close > sma50) & (df.Volume > vmean)

def e3(df):  # Cierre < SMA20 (bajista)
    sma20 = sma(df.Close, 20)
    return df.Close < sma20

def e4(df):  # Inside-day (rango de hoy dentro del rango previo)
    high_inside = df.High < df.High.shift()
    low_inside  = df.Low  > df.Low.shift()
    return high_inside & low_inside

STRATS = {
    "E1": e1,
    "E2": e2,
    "E3": e3,
    "E4": e4,
}

# ───────────────────────────── MAIN ───────────────────────────────
def main() -> None:
    hits = []
    for sym in SYMBOLS:
        df = yf_d(sym)
        if df.empty or len(df) < 60:
            continue

        for tag, f in STRATS.items():
            if to_bool(f(df)):
                hits.append(f"*{sym}*  → {tag}")
                break   # -- una señal por símbolo

    today = dt.datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    if hits:
        texto = f"📊 *Resumen diario – {today}*\n" + "\n".join(hits)
    else:
        texto = f"📊 *Resumen diario – {today}*\n_Sin señales válidas_"

    send(texto)

if __name__ == "__main__":
    main()
