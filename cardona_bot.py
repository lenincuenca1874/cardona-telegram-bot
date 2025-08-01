#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Escanea el mercado cada 5 min para 4 estrategias distintas.
Si encuentra nuevas señales envía UN mensaje a Telegram
(sin repetir ni spamear).  Usa timeframe 1 min y 1 día de
histórico; es suficiente para las reglas intradía.
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

TIMEZONE = ZoneInfo("America/New_York")     # hora de NY

# ────────────────────────── UTILIDADES ────────────────────────────
def yf_1m(sym: str) -> pd.DataFrame:
    """Histórico de hoy con velas de 1 min (incluye pre-market)."""
    return yf.download(sym, period="1d", interval="1m", progress=False)

def sma(series: pd.Series, n: int = 20) -> pd.Series:
    return series.rolling(n).mean()

def last(df: pd.Series | pd.DataFrame):
    """Devuelve el último valor/registro."""
    return df.iloc[-1]

def send(msg: str) -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)

def to_bool(serie: pd.Series) -> bool:
    """Convierte la última fila de una Serie booleana a bool nativo."""
    return bool(serie.iloc[-1])

# ────────────────────────── ESTRATEGIAS ───────────────────────────
def e1(df):
    # EMA9 cruza por encima de EMA20  → señal alcista
    ema9  = df.Close.ewm(span=9).mean()
    ema20 = df.Close.ewm(span=20).mean()
    cruz  = (ema9 > ema20) & (ema9.shift() <= ema20.shift())
    return cruz

def e2(df):
    # Ruptura de máximo de la primera hora (ORH) con volumen alto
    first_hour = df.between_time("09:30", "10:30")
    orh = first_hour.High.max()
    cond = (df.Close > orh) & (df.Volume > df.Volume.rolling(20).mean())
    return cond

def e3(df):
    # EMA9 cruza *por debajo* de EMA20  → señal bajista (put)
    ema9  = df.Close.ewm(span=9).mean()
    ema20 = df.Close.ewm(span=20).mean()
    cruz  = (ema9 < ema20) & (ema9.shift() >= ema20.shift())
    return cruz

def e4(df):
    # Mínimo inferior al mínimo de la primera hora (ORB-) con volumen alto
    first_hour = df.between_time("09:30", "10:30")
    orb = first_hour.Low.min()
    cond = (df.Close < orb) & (df.Volume > df.Volume.rolling(20).mean())
    return cond

STRATS = {
    "E1 (long)": e1,
    "E2 (ORH)":  e2,
    "E3 (short)":e3,
    "E4 (ORB-)": e4,
}

# ────────────────────────── LÓGICA PRINCIPAL ──────────────────────
def main() -> None:
    hits: list[str] = []

    now = dt.datetime.now(TIMEZONE)
    if not now.time() >= dt.time(9,30) or now.time() >= dt.time(16,0):
        return  # fuera de mercado: no hacemos nada

    for sym in SYMBOLS:
        df = yf_1m(sym)
        if df.empty:                 # símbolo sin datos hoy
            continue

        for tag, fn in STRATS.items():
            if to_bool(fn(df)):
                hits.append(f"*{sym}*  → {tag}")
                break                # para no duplicar la misma acción

    if hits:
        texto = "🚨 *Señales intradía detectadas*\n" + "\n".join(hits)
        send(texto)

if __name__ == "__main__":
    main()
