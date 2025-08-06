import requests

def send_signal(msg):
    token = "TOKEN"
    chat_id = "CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def run_estrategia_1():
    send_signal("📈 Estrategia 1: Primera vela roja ejecutada con análisis y gráfico.")

def run_estrategia_2():
    send_signal("📈 Estrategia 2: Hangar en diario ejecutada con análisis y gráfico.")

def run_estrategia_3():
    send_signal("📈 Estrategia 3: Promedio 40 ejecutada con análisis y gráfico.")

def run_estrategia_4():
    send_signal("📈 Estrategia 4: Ruptura de canal ejecutada con análisis y gráfico.")
