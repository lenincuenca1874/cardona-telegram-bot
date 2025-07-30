#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cardona Telegram Bot – 4 estrategias intradía
Envía alerta SOLO cuando se detecta una señal.
"""
import os, requests
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo
import yfinance as yf
import pandas as pd

TICKERS = [
    "SPY","QQQ","META","AAPL","AMZN","NFLX","MRNA","TSLA",
    "TNA","GLD","SLV","USO","BAC","CVX","XOM","NVDA"
]

TOKEN   = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NY_TZ   = ZoneInfo("America/New_York")

# Horarios NY para cada estrategia
VENTANA_E1 = (dtime(9,30),  dtime(10,1))   # Estrategia 1 – primera vela roja
VENTANA_E2 = (dtime(11,0),  dtime(16,0))   # Estrategia 2 – ruptura piso‑gap
VENTANA_E3 = (dtime(11,0),  dtime(16,0))   # Estrategia 3 – modelo 4 pasos
VENTANA_E4 = (dtime(15,55), dtime(16,1))   # Estrategia 4 – hángar diario

def now_ny():
    return datetime.now(tz=NY_TZ)

def send(msg:str):
    if not TOKEN or not CHAT_ID:
        print("[ERR] Faltan credenciales TG"); return
    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id":CHAT_ID,"text":msg})

# --------‑ funciones de cada estrategia ----------
def e1(df):
    return len(df)>=30 and df.Close.iloc[29] < df.Open.iloc[0]

def e2(df):
    return len(df)>=60 and df.Close.iloc[-1] < df.Low.iloc[:60].min()*0.999

def e3(df):
    if len(df)<60: return False
    ma20=df.Close.ewm(span=20).mean().iloc[-1]
    ma40=df.Close.ewm(span=40).mean().iloc[-1]
    px  =df.Close.iloc[-1]
    return ma20<ma40 and abs(px-ma40)<0.002*px

def e4(df_d):
    if len(df_d)<2: return False
    r=df_d.iloc[-1]
    cola=r.High-max(r.Close,r.Open)
    cuerpo=abs(r.Close-r.Open)
    return cola>=1.5*cuerpo and r.High>df_d.High.iloc[-2]

def main():
    ts=now_ny().time()
    alerts=[]
    for tkr in TICKERS:
        try:
            m1=yf.download(tkr,interval="1m",period="1d",auto_adjust=True,progress=False)
        except Exception:
            continue
        if m1.empty: continue

        if VENTANA_E1[0]<=ts<=VENTANA_E1[1] and e1(m1):
            alerts.append(f"📉 E1 Primera vela roja – {tkr}")
        if VENTANA_E2[0]<=ts<=VENTANA_E2[1] and e2(m1):
            alerts.append(f"📉 E2 Ruptura piso‑gap  – {tkr}")
        if VENTANA_E3[0]<=ts<=VENTANA_E3[1] and e3(m1):
            alerts.append(f"📈 E3 Modelo 4 pasos    – {tkr}")
        if VENTANA_E4[0]<=ts<=VENTANA_E4[1]:
            d1=yf.download(tkr,interval="1d",period="5d",auto_adjust=True,progress=False)
            if e4(d1): alerts.append(f"⚠️ E4 Hángar diario    – {tkr}")

    for a in alerts: send(a)

if __name__=="__main__":
    main()