name: realtime

on:
  schedule:
    - cron: '31 13-19 * * 1-5'  # Cada hora entre 9:31am y 3:31pm hora NY (13–19 UTC), lunes a viernes
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install yfinance pandas requests python-telegram-bot matplotlib

      - name: Run Cardona RealTime Bot
        run: python cardona_realtime.py
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
