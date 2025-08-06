
# 🤖 Bot Cardona – Señales de Trading Automatizadas

Este repositorio contiene un bot basado en las estrategias enseñadas por Alejandro Cardona para operar opciones en la bolsa de valores. El bot se ejecuta automáticamente usando **GitHub Actions**, analiza el mercado y envía señales y resúmenes directamente a Telegram.

---

## 📦 Contenido del proyecto

- `main.py`: Detecta la hora actual en NY y ejecuta la estrategia correspondiente o el resumen.
- `cardona_telegram_bot/`:
  - `cardona_realtime.py`: Contiene las funciones de las 4 estrategias.
  - `cardona_summary.py`: Genera y envía el resumen diario de señales.
- `.github/workflows/main.yml`: Automatiza la ejecución del bot según horarios predefinidos.
- `requirements.txt`: Lista de dependencias necesarias.
- `Procfile`: Solo requerido si deseas desplegar en Railway o VPS.

---

## 🔐 Configura tus Secrets en GitHub

Ve a: `Settings → Secrets → Actions` y añade:

- `TELEGRAM_TOKEN`: Token de tu bot de Telegram
- `TELEGRAM_CHAT_ID`: ID del canal o grupo donde recibirás las señales

---

## 🕒 Horarios de ejecución (hora de Nueva York)

| Hora       | Acción                                          |
|------------|-------------------------------------------------|
| 09:31 AM   | Estrategia 1 – Primera vela roja                |
| 10:00 AM   | Estrategia 2 – Hangar en diario                 |
| 12:00 PM   | Estrategia 3 – Promedio móvil 40                |
| 02:00 PM   | Estrategia 4 – Ruptura de canal                 |
| 03:45 PM   | 📊 Resumen final de señales del día             |

---

## 📬 Notificación fuera de horario

Si el bot se ejecuta en un horario que no corresponde a ninguna estrategia ni al resumen diario, recibirás un mensaje por Telegram indicando que no hubo acción.

---

## ✅ Créditos

Este bot está inspirado en las enseñanzas de Alejandro Cardona sobre trading de opciones y automatización inteligente del análisis técnico.

