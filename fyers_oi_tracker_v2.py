import time
import pandas as pd
import json
from fyers_apiv3 import fyersModel
from termcolor import colored
from tabulate import tabulate

import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

# ✅ In-memory storage for tracking OI changes
oi_history = {}

# ✅ Fetch Option Chain Data for a Symbol
def fetch_open_interest(symbol):
    data = {
        "symbol": symbol,  
        "strikecount": 10,  
        "timestamp": ""
    }

    try:
        response = fyers.optionchain(data=data)

        # 🛑 Handle API errors
        if response.get("s") != "ok":
            print(f"⚠️ API error: {response}")
            return None

        options_data = response.get("data", {}).get("optionsChain", [])

        total_call_oi = sum(opt["oi"] for opt in options_data if opt["option_type"] == "CE")
        total_put_oi = sum(opt["oi"] for opt in options_data if opt["option_type"] == "PE")

        return total_call_oi, total_put_oi

    except Exception as e:
        print(f"❌ Error fetching OI for {symbol}: {e}")
        return None

# ✅ Function to color % Change values
def format_percentage(value):
    if value > 0:
        return colored(f"{value:.2f}%", "green")
    elif value < 0:
        return colored(f"{value:.2f}%", "red")
    else:
        return f"{value:.2f}%"

# ✅ Track OI Changes Every 5 Minutes
def track_oi(symbols):
    while True:
        table_data = []
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        for symbol in symbols:
            oi_data = fetch_open_interest(symbol)
            if oi_data:
                total_call_oi, total_put_oi = oi_data

                if symbol not in oi_history:
                    oi_history[symbol] = []

                prev_oi = oi_history[symbol][-1] if oi_history[symbol] else {"call_oi": 0, "put_oi": 0}
                call_oi_change = total_call_oi - prev_oi["call_oi"]
                put_oi_change = total_put_oi - prev_oi["put_oi"]

                call_oi_pct = (call_oi_change / prev_oi["call_oi"] * 100) if prev_oi["call_oi"] else 0
                put_oi_pct = (put_oi_change / prev_oi["put_oi"] * 100) if prev_oi["put_oi"] else 0

                # ✅ Apply color formatting to % Change
                call_oi_pct_str = format_percentage(call_oi_pct)
                put_oi_pct_str = format_percentage(put_oi_pct)

                # ✅ Determine Trend
                trend = "📈 Call Increasing" if call_oi_change > 0 else "📉 Call Decreasing"
                trend += " | 📈 Put Increasing" if put_oi_change > 0 else " | 📉 Put Decreasing"

                # ✅ Store in history
                oi_history[symbol].append({
                    "Time": timestamp,
                    "call_oi": total_call_oi,
                    "put_oi": total_put_oi
                })

                # ✅ Store Data for Tabular Display
                table_data.append([symbol, total_call_oi, total_put_oi, call_oi_change, put_oi_change, call_oi_pct_str, put_oi_pct_str, trend])

        # ✅ Print Tabular Output
        print(f"\n📊 OI Tracking Data | {timestamp}\n")
        headers = ["Symbol", "Total Call OI", "Total Put OI", "Call OI Change", "Put OI Change", "% Change Call OI", "% Change Put OI", "Trend"]
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        # 🕒 Wait for 5 minutes before next fetch
        time.sleep(3)

# ✅ List of Option Symbols to Track
symbols_to_track = [
    "NSE:BANKNIFTY25FEB49000CE",
    "NSE:BANKNIFTY25FEB49000PE",
    "NSE:NIFTY25FEB20000CE",
    "NSE:NIFTY25FEB20000PE"
]

# ✅ Start Tracking OI for Multiple Symbols
track_oi(symbols_to_track)
