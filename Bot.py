bot.py
import os import json import urllib.request import urllib.parse import math
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"] CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
def get_gold_data(): url = ( "https://query1.finance.yahoo.com/v8/finance/chart/GC=F" "?interval=1h&period1=1760000000&period2=1790000000" )
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req, timeout=20) as response:
    data = json.loads(response.read().decode())

result = data["chart"]["result"][0]
prices = result["indicators"]["quote"][0]["close"]
prices = [p for p in prices if p is not None]

return prices
def ema(values, period): if len(values) < period: return None
multiplier = 2 / (period + 1)
value = sum(values[:period]) / period

for price in values[period:]:
    value = (price - value) * multiplier + value

return value
def rsi(values, period=14): if len(values) <= period: return None
gains = []
losses = []

for i in range(1, len(values)):
    change = values[i] - values[i - 1]
    gains.append(max(change, 0))
    losses.append(max(-change, 0))

avg_gain = sum(gains[:period]) / period
avg_loss = sum(losses[:period]) / period

for i in range(period, len(gains)):
    avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
    avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

if avg_loss == 0:
    return 100

rs = avg_gain / avg_loss
return 100 - (100 / (1 + rs))
def make_signal(): prices = get_gold_data()
price = prices[-1]
ema20 = ema(prices, 20)
ema50 = ema(prices, 50)
rsi_value = rsi(prices)

if ema20 is None or ema50 is None or rsi_value is None:
    return "NO TRADE"

if ema20 > ema50 and rsi_value >= 50 and rsi_value <= 70:
    entry = price
    sl = price - 5
    tp1 = price + 7
    tp2 = price + 12

    return (
        "🟢 XAUUSD BUY\n\n"
        f"Entry: {entry:.2f}\n"
        f"SL: {sl:.2f}\n"
        f"TP1: {tp1:.2f}\n"
        f"TP2: {tp2:.2f}\n\n"
        f"EMA20: {ema20:.2f}\n"
        f"EMA50: {ema50:.2f}\n"
        f"RSI: {rsi_value:.1f}\n\n"
        "⚠️ Risk management is required."
    )

if ema20 < ema50 and rsi_value >= 30 and rsi_value <= 50:
    entry = price
    sl = price + 5
    tp1 = price - 7
    tp2 = price - 12

    return (
        "🔴 XAUUSD SELL\n\n"
        f"Entry: {entry:.2f}\n"
        f"SL: {sl:.2f}\n"
        f"TP1: {tp1:.2f}\n"
        f"TP2: {tp2:.2f}\n\n"
        f"EMA20: {ema20:.2f}\n"
        f"EMA50: {ema50:.2f}\n"
        f"RSI: {rsi_value:.1f}\n\n"
        "⚠️ Risk management is required."
    )

return (
    "⚪ XAUUSD NO TRADE\n\n"
    "Setup is not strong enough.\n"
    "Wait for a clearer signal."
)
def send_telegram(message): url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": CHAT_ID,
    "text": message
}).encode()

request = urllib.request.Request(url, data=data)

with urllib.request.urlopen(request, timeout=20) as response:
    return response.read().decode()
if name == "main": signal = make_signal() send_telegram(signal) print(signal)
