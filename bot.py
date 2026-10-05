import os
import json
import urllib.request
import urllib.parse


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def get_gold_prices():
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
        "?range=30d&interval=1h"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode())

    result = data["chart"]["result"][0]
    prices = result["indicators"]["quote"][0]["close"]

    return [float(x) for x in prices if x is not None]


def ema(values, period):
    if len(values) < period:
        return None

    multiplier = 2 / (period + 1)
    value = sum(values[:period]) / period

    for price in values[period:]:
        value = (price - value) * multiplier + value

    return value


def rsi(values, period=14):
    if len(values) <= period:
        return None

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


def make_signal():
    prices = get_gold_prices()

    if len(prices) < 50:
        return "NO TRADE"

    price = prices[-1]

    ema20 = ema(prices, 20)
    ema50 = ema(prices, 50)
    rsi_value = rsi(prices)

    if ema20 is None or ema50 is None or rsi_value is None:
        return "NO TRADE"

    if ema20 > ema50 and rsi_value >= 55:
        signal = "BUY"
    elif ema20 < ema50 and rsi_value <= 45:
        signal = "SELL"
    else:
        signal = "NO TRADE"

    return (
        "XAUUSD SIGNAL\n"
        "━━━━━━━━━━━━━━\n"
        f"Signal: {signal}\n"
        f"Price: {price:.2f}\n"
        f"EMA20: {ema20:.2f}\n"
        f"EMA50: {ema50:.2f}\n"
        f"RSI14: {rsi_value:.2f}\n"
        "━━━━━━━━━━━━━━\n"
        "⚠️ For analysis only. Trade with risk control."
    )


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode()


def main():
    if not TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN")

    if not CHAT_ID:
        raise ValueError("Missing TELEGRAM_CHAT_ID")

    message = make_signal()
    send_telegram(message)

    print(message)


if __name__ == "__main__":
    main()
