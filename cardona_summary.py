#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cardona_summary.py  –  Resumen diario con gráfico
• Para cada símbolo que dispare señal:
      • Mensaje de texto (estrategia, hora, spot, strike, rationale)
      • Gráfico PNG adjunto
• Si no hay señales → Mensaje “Sin señales válidas”
"""

import os, datetime, tempfile, requests, pandas as pd, telegram
import yfinance as yf
import matplotlib
matplotlib.use("Agg")                # backend sin interfaz gráfica
import matplotlib.pyplot as plt

# ─────────── Configuración básica ───────────
TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SYMBOLS = [
    "SPY","QQQ","AAPL","META","AMZN","NFLX","TSLA","NVDA",
    "MRNA","BAC","TNA","GLD","SLV","USO","XOM","CVX"
]

TIMEZONE = "America/New_York"
TZ = datetime.timezone(datetime.timedelta(hours=-4), TIMEZONE)

# ─────────── Estrategias (ejemplo) ───────────
def gap_ajista_alza(df: pd.DataFrame) -> bool:
    """
    Gap alcista tras vela roja:
      • La apertura (t) > máx (t-1)   AND
      • El cierre (t-1) < apertura (t-1)  (vela roja previa)
    """
    if len(df) < 2: return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    return (curr["Open"] > prev["High"]) and (prev["Close"] < prev["Open"])

def strike_sugerido(spot: float, direction: str) -> float:
    pct = 1.02 if direction == "CALL" else 0.98
    return round(spot * pct, 2)

# ─────────── Utilidades ───────────
def yf_hourly(sym: str) -> pd.DataFrame:
    return yf.download(sym, period="7d", interval="60m",
                       auto_adjust=True, progress=False)

def spot(sym: str) -> float:
    return float(
        yf.download(sym, period="1d", interval="1m",
                    auto_adjust=True, progress=False)["Close"].iloc[-1])

def make_chart(sym: str, df: pd.DataFrame, signal_ts: pd.Timestamp) -> str:
    """
    Genera un PNG en /tmp y devuelve la ruta
    """
    # recortamos a los últimos 5 días para un gráfico compacto
    df = df.tail(5*24)
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df.index, df["Close"], label="Close", lw=1.2)
    # señal
    ax.scatter(signal_ts, df["Close"].iloc[-1],
               color="red", zorder=5, label="Señal")
    ax.set_title(f"{sym} – Close 1 h")
    ax.legend()
    ax.grid(True, alpha=.3)
    # formato fechas
    fig.autofmt_xdate()

    tmp_file = tempfile.NamedTemporaryFile(
        suffix=f"_{sym}.png", delete=False)
    fig.savefig(tmp_file.name, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return tmp_file.name

# ─────────── Principal ───────────
def main():
    hoy = datetime.datetime.now(TZ).strftime("%Y-%m-%d")
    bot = telegram.Bot(TOKEN)

    hits = []
    for sym in SYMBOLS:
        df = yf_hourly(sym)
        if df.empty: continue

        # Estrategia 1 (ejemplo)
        if gap_ajista_alza(df):
            ahora   = datetime.datetime.now(TZ).strftime("%H:%M")
            ts_señal = df.index[-1]
            precio  = spot(sym)
            hits.append({
                "sym": sym,
                "hora": ahora,
                "estrategia": "Gap alcista",
                "dir": "CALL",
                "spot": precio,
                "strike": strike_sugerido(precio, "CALL"),
                "rationale": (
                    "Abrió por encima del máximo previo tras vela roja."
                ),
                "chart": make_chart(sym, df, ts_señal)
            })

        # ↳  Añade aquí tus otras 3 estrategias …

    # ── Envío de mensajes ─────────────────────
    if not hits:
        bot.send_message(
            chat_id=CHAT_ID,
            text=f"📆 *{hoy}*\nSin señales válidas.",
            parse_mode="Markdown")
        return

    for h in hits:
        texto = "\n".join([
            f"📆 *{hoy}*  —  `{h['hora']}`",
            f"*{h['sym']}*  ({h['estrategia']})",
            f"• Dirección: *{h['dir']}*",
            f"• Spot: `{h['spot']:.2f}` | Strike: `{h['strike']}`",
            f"• Por qué: _{h['rationale']}_"
        ])
        bot.send_message(chat_id=CHAT_ID,
                         text=texto,
                         parse_mode="Markdown")
        # Enviamos gráfico
        bot.send_photo(chat_id=CHAT_ID,
                       photo=open(h["chart"], "rb"),
                       caption=f"{h['sym']} – gráfico 1 h")

if __name__ == "__main__":
    main()
