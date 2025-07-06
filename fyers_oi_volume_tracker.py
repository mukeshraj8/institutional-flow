import time
import pandas as pd
import json
from fyers_apiv3 import fyersModel
from termcolor import colored
import os
from tabulate import tabulate

# ✅ Load Access Token
def load_access_token():
    try:
        with open("access_token.json", "r") as file:
            data = json.load(file)
            return data.get("access_token")
    except Exception as e:
        print(f"❌ Error loading access token: {e}")
        return None

# ✅ Initialize Fyers API
access_token = load_access_token()
if not access_token:
    print("❌ Missing access token! Exiting.")
    exit()

fyers = fyersModel.FyersModel(client_id="YOUR_CLIENT_ID", is_async=False, token=access_token)

# ✅ In-memory storage for OI, Volume, and Least Volume tracking
oi_history = {}
volume_history = {}
least_volume_today = {}  # Stores the least volume observed so far

# ✅ Function to Fetch Open Interest (OI) & Volume for Any Symbol
def fetch_open_interest(symbol):
    data = {
        "symbol": symbol,
        "strikecount": 10,
        "timestamp": ""
    }

    try:
        response = fyers.optionchain(data=data)

        if response.get("s") != "ok":
            print(f"⚠️ API error for {symbol}: {response}")
            return None

        options_data = response.get("data", {}).get("optionsChain", [])

        if not options_data:
            print(f"⚠️ No options data found for {symbol}. Response: {response}")
            return None

        total_call_oi, total_put_oi = 0, 0
        total_call_volume, total_put_volume = 0, 0

        for opt in options_data:
            oi = opt.get("oi", 0)
            volume = opt.get("volume", 0)
            opt_type = opt.get("option_type")  

            if opt_type == "CE":
                total_call_oi += oi
                total_call_volume += volume
            elif opt_type == "PE":
                total_put_oi += oi
                total_put_volume += volume

        return {
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "total_call_volume": total_call_volume,
            "total_put_volume": total_put_volume
        }

    except Exception as e:
        print(f"❌ Exception while fetching OI for {symbol}: {e}")
        return None

# ✅ Function to Track OI Changes Every 5 Minutes for Multiple Symbols
def track_oi(symbols):
    while True:
        os.system("cls" if os.name == "nt" else "clear")  
        print("\n📊 **Open Interest & Volume Tracker**\n")

        table_data = []  

        for symbol in symbols:
            oi_data = fetch_open_interest(symbol)
            timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            if oi_data:
                prev_data = oi_history.get(symbol, {})
                prev_volume = volume_history.get(symbol, {})

                call_oi_change = oi_data["total_call_oi"] - prev_data.get("total_call_oi", 0)
                put_oi_change = oi_data["total_put_oi"] - prev_data.get("total_put_oi", 0)

                call_oi_change_pct = (call_oi_change / prev_data.get("total_call_oi", 1)) * 100 if prev_data.get("total_call_oi", 0) else 0
                put_oi_change_pct = (put_oi_change / prev_data.get("total_put_oi", 1)) * 100 if prev_data.get("total_put_oi", 0) else 0

                call_volume_change = oi_data["total_call_volume"] - prev_volume.get("total_call_volume", 0)
                put_volume_change = oi_data["total_put_volume"] - prev_volume.get("total_put_volume", 0)

                total_volume = oi_data["total_call_volume"] + oi_data["total_put_volume"]

                # ✅ Track the least volume seen today
                if symbol not in least_volume_today:
                    least_volume_today[symbol] = total_volume
                else:
                    least_volume_today[symbol] = min(least_volume_today[symbol], total_volume)

                least_vol = least_volume_today[symbol]

                trend = []
                if call_oi_change > 0:
                    trend.append("📈 Call OI ↑")
                elif call_oi_change < 0:
                    trend.append("📉 Call OI ↓")

                if put_oi_change > 0:
                    trend.append("📈 Put OI ↑")
                elif put_oi_change < 0:
                    trend.append("📉 Put OI ↓")

                trend_text = ", ".join(trend) if trend else "No Major Change"

                oi_history[symbol] = oi_data
                volume_history[symbol] = oi_data

                call_oi_change_pct_color = colored(f"{call_oi_change_pct:.2f}%", "green" if call_oi_change_pct > 0 else "red")
                put_oi_change_pct_color = colored(f"{put_oi_change_pct:.2f}%", "green" if put_oi_change_pct > 0 else "red")

                volume_trend = "⬆️ Increased" if (call_volume_change + put_volume_change) > 0 else "⬇️ Decreased"

                # ✅ Append data to table
                table_data.append([
                    symbol,
                    oi_data["total_call_oi"],
                    oi_data["total_put_oi"],
                    call_oi_change,
                    put_oi_change,
                    call_oi_change_pct_color,
                    put_oi_change_pct_color,
                    trend_text,
                    total_volume,
                    volume_trend,
                    least_vol
                ])

            else:
                table_data.append([symbol, "⚠️ Failed to fetch data"] + [""] * 9)

        headers = [
            "Symbol", "Call OI", "Put OI", "Δ Call OI", "Δ Put OI",
            "% Δ Call OI", "% Δ Put OI", "Trend", "5-Min Volume", "Volume Trend", "Least Volume Today"
        ]
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

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
