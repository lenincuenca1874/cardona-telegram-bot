# cardona_telegram_bot.py
"""
Telegram bot that scans the US market every trading day for Alejandro Cardona's
**Estrategia 1: Primera vela roja de apertura** and sends a signal + chart to a
Telegram chat.

Free‑tier stack:
- **GitHub + GitHub Actions (cron)** – scheduler / runner (no server bill).
- **python‑telegram‑bot** – Bot API wrapper (free).
- **yfinance** – free market data (1 minute).  NOTE: Data is 15 min delayed for
  free users; still usable for educational signals.
- **matplotlib / mplfinance** – local chart rendering.

Secrets required (set in GitHub repo → *Settings › Secrets › Actions*):
- `TELEGRAM_TOKEN` – Bot token from @BotFather.
- `TELEGRAM_CHAT_ID` – Chat or channel ID that will receive the alerts.

Run locally → `python cardona_telegram_bot.py`
GitHub‑Actions workflow ( .github/workflows/bot.yml ) will run `python
cardona_telegram_bot.py` at **14:05 UTC** → 10:05 ET.
"""

from __future__ import annotations

import io
import os
import sys
import datetime as dt
from dataclasses import dataclass
from typing import List
import pytz
import pandas as pd
import yfinance as yf
import mplfinance as mpf
from telegram import Bot

# -------------------- CONFIG -------------------------------------------------

ASSETS = {
    # symbol: (min_price, max_price, spot_strike_distance)
    "SPY": (0.25, 0.30, 10),
    "QQQ": (0.25, 0.30, 10),
    "META": (0.45, 0.80, 25),  # distance = 20‑25 → use max for calc
    "AAPL": (0.45, 0.80, 4),
    "AMZN": (0.60, 0.80, 8),
    "NFLX": (1.50, 2.50, 15),
    "MRNA": (1.00, 2.00, 15),
    "TSLA": (2.50, 2.50, 10),
    "TNA": (0.60, 0.80, 13),
    "GLD": (0.60, 0.80, 4),
    "SLV": (0.10, 0.20, 2),
    "USO": (0.10, 0.20, 3),
    "BAC": (0.10, 0.20, 2),
    "CVX": (0.60, 0.80, 5),
    "XOM": (0.60, 0.80, 5),
    "NVDA": (0.60, 0.80, 9),
}

VOLUME_MIN: dict[str, int] = {
    "SPY": 20_000_000,
    "QQQ": 20_000_000,
    "META": 3_000_000,
    "AAPL": 20_000_000,
    "AMZN": 16_000_000,
    "NFLX": 1_000_000,
    "MRNA": 2_000_000,
    "TSLA": 15_000_000,
    "TNA": 2_000_000,
    "GLD": 2_000_000,
    "SLV": 10_000_000,
    "USO": 1_000_000,
    "BAC": 10_000_000,
    "CVX": 2_000_000,
    "XOM": 4_000_000,
    "NVDA": 120_000_000,
}

ET = pytz.timezone("US/Eastern")

# -----------------------------------------------------------------------------
@dataclass
class Signal:
    symbol: str
    timestamp: dt.datetime  # 10:00 candle close (ET)
    spot: float
    strike: float
    option_price_range: tuple[float, float]
    chart_png: bytes

# -----------------------------------------------------------------------------

def fetch_intraday(symbol: str, day: dt.date) -> pd.DataFrame:
    """Download 1‑minute data for *day* (local ET date)."""
    start = dt.datetime.combine(day, dt.time(9, 25), tzinfo=ET)
    end = dt.datetime.combine(day, dt.time(10, 5), tzinfo=ET)
    df = yf.download(symbol, interval="1m", start=start, end=end, progress=False, threads=False)
    if df.empty:
        raise ValueError(f"No data for {symbol} on {day}")
    df.index = df.index.tz_convert(ET)
    return df


def is_first_red(df: pd.DataFrame) -> bool:
    """Return True if the 9:30–9:35 candle is red."""
    first5 = df.between_time("09:30", "09:34")
    if first5.empty:
        return False
    open_ = first5.iloc[0]["Open"]
    close = first5.iloc[-1]["Close"]
    return close < open_


def is_ten_am_red(df: pd.DataFrame) -> bool:
    candle10 = df.at_time("10:00")
    if candle10.empty:
        return False
    row = candle10.iloc[0]
    return row["Close"] < row["Open"]


def make_chart(df: pd.DataFrame, symbol: str) -> bytes:
    mc = mpf.make_marketcolors(up="#26a69a", down="#ef5350", inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)
    buf = io.BytesIO()
    mpf.plot(df,
             type="candle",
             style=s,
             title=f"{symbol} — 1‑min chart (09:30‑10:05 ET)",
             ylabel="Price ($)",
             datetime_format="%H:%M",
             xrotation=20,
             savefig=dict(fname=buf, format="png"))
    buf.seek(0)
    return buf.read()


def scan_symbol(symbol: str, day: dt.date) -> Signal | None:
    try:
        df = fetch_intraday(symbol, day)
    except ValueError:
        return None

    if not (is_first_red(df) and is_ten_am_red(df)):
        return None

    # Check volume so far (approx)
    vol = df["Volume"].sum()
    if vol < VOLUME_MIN.get(symbol, 0):
        return None

    spot = df.iloc[-1]["Close"]
    distance = ASSETS[symbol][2]
    strike = round(spot - distance, 0)

    chart = make_chart(df, symbol)
    return Signal(
        symbol=symbol,
        timestamp=df.index[-1].to_pydatetime(),
        spot=float(spot),
        strike=strike,
        option_price_range=(ASSETS[symbol][0], ASSETS[symbol][1]),
        chart_png=chart,
    )

# -----------------------------------------------------------------------------

def build_message(sig: Signal) -> str:
    min_p, max_p = sig.option_price_range
    ts = sig.timestamp.astimezone(ET).strftime("%H:%M")
    return (
        f"🚨 *Señal Estrategia 1 – Primera vela roja de apertura*\n\n"
        f"*Activo:* `{sig.symbol}`\n"
        f"*Hora:* {ts} ET\n"
        f"*Spot:* ${sig.spot:.2f}  →  *Strike sugerido:* {sig.strike}\n"
        f"*Precio contrato PUT:* ${min_p:.2f} – ${max_p:.2f}\n"
        f"*Distancia spot‑strike:* ~{ASSETS[sig.symbol][2]} pts\n"
        f"#CardonaBot #Estrategia1"
    )

# -----------------------------------------------------------------------------

def main() -> None:
    today = dt.datetime.now(ET).date()
    bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    signals: List[Signal] = []
    for symbol in ASSETS.keys():
        sig = scan_symbol(symbol, today)
        if sig:
            signals.append(sig)

    if not signals:
        print("No Strategy 1 signals today")
        return

    for s in signals:
        msg = build_message(s)
        bot.send_photo(chat_id=chat_id, photo=s.chart_png, caption=msg, parse_mode="Markdown")
        print(f"Signal sent for {s.symbol}")

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        raise
