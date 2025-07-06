import time
import pandas as pd
from fyers_apiv3 import fyersModel
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import print
from rich.text import Text

import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

# ✅ In-memory storage for OI, Volume, and Least Volume tracking
oi_history = {}
volume_history = {}
least_volume_today = {}
console = Console()  # Rich Console for table display

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
            return None

        options_data = response.get("data", {}).get("optionsChain", [])

        if not options_data:
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

    except Exception:
        return None

# ✅ Function to Generate Table Structure (Without Placeholder Rows)
def generate_table():
    table = Table()
    table.add_column("Symbol", style="bold cyan")
    table.add_column("Call OI", justify="right")
    table.add_column("Put OI", justify="right")
    table.add_column("Δ Call OI", justify="right")
    table.add_column("Δ Put OI", justify="right")
    table.add_column("% Δ Call OI", justify="right")
    table.add_column("% Δ Put OI", justify="right")
    table.add_column("Trend", justify="left")
    table.add_column("5-Min Volume", justify="right")
    table.add_column("Volume Trend", justify="left")
    table.add_column("Least Volume Today", justify="right")

    return table  # ⛔ No pre-filled rows


def track_oi(symbols):
    with Live(generate_table(), console=console, refresh_per_second=1) as live_table:
        while True:
            table = generate_table()  # ✅ Fixed table structure

            for symbol in symbols:
                oi_data = fetch_open_interest(symbol)

                if oi_data:
                    prev_data = oi_history.get(symbol, {})
                    prev_volume = volume_history.get(symbol, {})

                    # ✅ Calculate OI & Volume Changes
                    call_oi_change = oi_data["total_call_oi"] - prev_data.get("total_call_oi", 0)
                    put_oi_change = oi_data["total_put_oi"] - prev_data.get("total_put_oi", 0)
                    total_volume = oi_data["total_call_volume"] + oi_data["total_put_volume"]

                    # ✅ Percentage Change Calculation
                    call_oi_change_pct = (call_oi_change / prev_data.get("total_call_oi", 1)) * 100 if prev_data.get("total_call_oi", 0) else 0
                    put_oi_change_pct = (put_oi_change / prev_data.get("total_put_oi", 1)) * 100 if prev_data.get("total_put_oi", 0) else 0

                    # ✅ Track Least Volume
                    least_volume_today[symbol] = min(least_volume_today.get(symbol, total_volume), total_volume)

                    # ✅ Trend Analysis
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

                    # ✅ Color Formatting Based on Value Changes
                    def format_value(value):
                        if value > 0:
                            return Text(str(value), style="green")  # 🟢 Positive (Green)
                        elif value < 0:
                            return Text(str(value), style="red")  # 🔴 Negative (Red)
                        return str(value)  # ⚪ Unchanged (White)

                    def format_percentage(value):
                        if value > 0:
                            return Text(f"{value:.2f}%", style="green")  # 🟢 Positive (Green)
                        elif value < 0:
                            return Text(f"{value:.2f}%", style="red")  # 🔴 Negative (Red)
                        return f"{value:.2f}%"  # ⚪ Unchanged (White)

                    # ✅ Determine Volume Trend
                    volume_trend = (
                        Text("⬆️ Increased", style="green") if total_volume > prev_volume.get("total_call_volume", 0) + prev_volume.get("total_put_volume", 0)
                        else Text("⬇️ Decreased", style="red") if total_volume < prev_volume.get("total_call_volume", 0) + prev_volume.get("total_put_volume", 0)
                        else "No Change"
                    )

                    # ✅ Update History for Next Iteration
                    oi_history[symbol] = oi_data
                    volume_history[symbol] = oi_data

                    # ✅ Add Row to Table
                    table.add_row(
                        symbol,
                        str(oi_data["total_call_oi"]),
                        str(oi_data["total_put_oi"]),
                        format_value(call_oi_change),
                        format_value(put_oi_change),
                        format_percentage(call_oi_change_pct),
                        format_percentage(put_oi_change_pct),
                        trend_text,
                        format_value(total_volume),
                        volume_trend,
                        str(least_volume_today[symbol])
                    )
                else:
                    table.add_row(symbol, "⚠️ Failed to fetch data", "-", "-", "-", "-", "-", "-", "-", "-", "-")

            # ✅ Update Live Table Without Blinking
            live_table.update(table)
            time.sleep(5)  # Fetch new data every 5 seconds


# ✅ List of Option Symbols to Track
symbols_to_track = [
    "NSE:BANKNIFTY25FEB49000CE",
    "NSE:BANKNIFTY25FEB49000PE",
    "NSE:NIFTY25FEB20000CE",
    "NSE:NIFTY25FEB20000PE",
    "NSE:NIFTY25FEBFUT",
    "NSE:BANKNIFTY25FEBFUT"
]

# ✅ Start Tracking OI for Multiple Symbols
track_oi(symbols_to_track)
