import numpy as np
import talib
from fyers_data import get_ohlc, get_open_interest

# Strategy Parameters
RSI_PERIOD = 14
BREAKOUT_THRESHOLD = 0.5  # 0.5% above/below previous high/low

def calculate_rsi(data):
    """ Calculate RSI using TA-Lib """
    return talib.RSI(data['close'], timeperiod=RSI_PERIOD)

def breakout_signal(data):
    """ Identify Breakout Levels """
    prev_high = data['high'].iloc[-2]
    prev_low = data['low'].iloc[-2]
    breakout_up = prev_high * (1 + BREAKOUT_THRESHOLD / 100)
    breakout_down = prev_low * (1 - BREAKOUT_THRESHOLD / 100)
    return breakout_up, breakout_down

def check_trade_condition(data, oi_data):
    """ Check if breakout + RSI + OI confirm trade """
    rsi = calculate_rsi(data)
    breakout_up, breakout_down = breakout_signal(data)
    latest_close = data['close'].iloc[-1]
    
    if latest_close > breakout_up and rsi.iloc[-1] > 50 and oi_data > 100000:
        return "BUY"
    elif latest_close < breakout_down and rsi.iloc[-1] < 50 and oi_data > 100000:
        return "SELL"
    return "HOLD"

# Fetch Data
data = get_ohlc()
oi_data = get_open_interest()

# Check Trade Condition
trade_signal = check_trade_condition(data, oi_data)
print(f"🚀 Trade Signal: {trade_signal}")
