#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumen diario Cardona Bot"""
import os, requests
from datetime import datetime
from zoneinfo import ZoneInfo
import yfinance as yf
import pandas as pd

TICKERS=[
    "SPY","QQQ","META","AAPL","AMZN","NFLX","MRNA","TSLA",
    "TNA","GLD","SLV","USO","BAC","CVX","XOM","NVDA"
]
TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")
NY=ZoneInfo("America/New_York")

def send(t):
    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url,data={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"})

def e1(df):return len(df)>=30 and df.Close.iloc[29]<df.Open.iloc[0]
def e2(df):return len(df)>=60 and df.Close.iloc[-1]<df.Low.iloc[:60].min()*0.999
def e3(df):
    if len(df)<60:return False
    m20=df.Close.ewm(span=20).mean().iloc[-1]
    m40=df.Close.ewm(span=40).mean().iloc[-1]
    px=df.Close.iloc[-1]
    return m20<m40 and abs(px-m40)<0.002*px
def e4(d):
    if len(d)<2:return False
    r=d.iloc[-1];c=abs(r.Close-r.Open);cola=r.High-max(r.Close,r.Open)
    return cola>=1.5*c and r.High>d.High.iloc[-2]

def hoy():return datetime.now(tz=NY).strftime("%Y-%m-%d")

def main():
    hits=[]
    for t in TICKERS:
        m1=yf.download(t,interval="1m",period="1d",progress=False,auto_adjust=True)
        if m1.empty:continue
        if e1(m1):hits.append(f"📉 *E1* {t}")
        if e2(m1):hits.append(f"📉 *E2* {t}")
        if e3(m1):hits.append(f"📈 *E3* {t}")
        d1=yf.download(t,interval="1d",period="5d",progress=False,auto_adjust=True)
        if e4(d1):hits.append(f"⚠️ *E4* {t}")
    txt="📊 *Resumen "+hoy()+"*\n"+("\n".join(hits) if hits else "🚫 Sin señales hoy.")
    send(txt)

if __name__=="__main__":
    main()