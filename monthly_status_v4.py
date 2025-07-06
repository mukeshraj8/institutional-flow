import requests
from datetime import datetime, timedelta
import pandas as pd
from fyers_apiv3 import fyersModel
from fyers_ltp_fetcher import FyersLTPFetcher
#from fyers_trade_symbols import SYMBOL_MAP
from fyers_trade_symbols_test import SYMBOL_MAP
import time
import fyers_symbols_validator as symbValidator

#fyersv\Scripts\activate

import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

THRESHOLD_VALUES = {
    "index": {"a": 0.75, "b": 0.75, "c": 0.15},
    "stock": {"a": 2.50, "b": 2.00, "c": 1.00},
    "currency": {"a": 0.15, "b": 0.05, "c": 0.05},
    "gold": {"a": 0.50, "b": 0.50, "c": 0.12},
    "silver": {"a": 0.70, "b": 0.70, "c": 0.15},
    "crudeoil": {"a": 2.00, "b": 1.50, "c": 0.30},
    "naturalgas": {"a": 2.00, "b": 2.00, "c": 0.50},
}

ltp_fetcher = FyersLTPFetcher(credentials.get_access_token())


def fetch_historical_data(symbol, start_date, end_date, interval="D"):
    data = fyers.history(
        {"symbol": symbol, "resolution": interval, "date_format": 1,
         "range_from": start_date, "range_to": end_date}
    )

    if data.get("code") == 429:
        print(f"Rate limit exceeded for {symbol}")
        raise Exception(f"Fetch Rate limit exceeded...")
        
    if data['s'] != 'ok':
        raise Exception(f"Error fetching data: {data}")
    return pd.DataFrame(data['candles'], columns=["timestamp", "open", "high", "low", "close", "volume"])


def fetch_ltp_for_symbols(symbols):
    ltp_data = {}
    batch_size = 50  # Process in batches to avoid rate limits

    for i in range(0, len(symbols), batch_size):
        try:
            #symbol_batch = [f"NSE:{symbol}" for symbol in symbols[i:i+batch_size]]  # Proper formatting
            symbol_batch = [f"{symbol}" for symbol in symbols[i:i+batch_size]]  # Proper formatting
            response = fyers.quotes({"symbols": ",".join(symbol_batch)})  # Pass as a comma-separated string
            time.sleep(1)  # Prevent hitting rate limits

            if response.get("s") == "ok":
                for item in response.get("d", []):
                    #symbol_name = item["n"].replace("NSE:", "").strip()
                    symbol_name = item["n"]
                    if item["v"].get("s") == "error":
                        print(f"Error for {symbol_name}: {item['v'].get('errmsg', 'Unknown error')}")
                    else:
                        ltp_data[symbol_name] = item["v"].get("lp", None)
                        print(f"{symbol_name}: {ltp_data[symbol_name]}")
            else:
                print(f"Unexpected API response: {response}")

        except Exception as e:
            print(f"Error fetching LTP batch: {e}")

    return ltp_data


def fetch_ltp_for_symbol(symbol):
    """
    Fetch the LTP for a given trading symbol.

    Parameters:
        symbol (str): The trading symbol (e.g., "NSE:SBIN-EQ").
    Returns:
        float: The last traded price of the symbol or None if not available.
    """
    ltp_fetcher.subscribe_to_symbol(symbol)
    time.sleep(1)  # Allow some time to receive LTP data
    ltp = ltp_fetcher.get_ltp()
    return ltp


def check_reversal_conditions(symbol, price, pwh, pwl, cwh, cwl):
    """Check for Bullish or Bearish reversal conditions."""
    thresholds = get_thresholds(symbol)
    c = thresholds["c"]
    # print(f"c for {symbol}: {c}")

    bullish_reversal = max(pwh, cwh) + (max(pwh, cwh) * c / 100)
    bearish_reversal = min(pwl, cwl) - (min(pwl, cwl) * c / 100)

    if price >= bullish_reversal:
        return "Bullish Reversal"
    
    elif price <= bearish_reversal:
        return "Bearish Reversal"
    
    return None

def calculate_previous_status(symbol):
    today = datetime.now()
    months_back = 2
    while True:
        first_day_of_month = datetime(today.year, today.month, 1)
        last_day_prev = first_day_of_month - timedelta(days=1)
        first_day_prev = datetime(last_day_prev.year, last_day_prev.month, 1)
        
        data = fetch_historical_data(symbol, first_day_prev.strftime('%Y-%m-%d'), last_day_prev.strftime('%Y-%m-%d'))
        pmh, pml = data['high'].max(), data['low'].min()

        price = fetch_ltp_for_symbol(symbol)
        bullish_value, bearish_value, bullish_favour, bearish_favour = calculate_thresholds(symbol, pmh, pml)

        if price >= bullish_favour:
            return "Bullish Confirmed"
        elif price >= bullish_value:
            return "Bullish"
        elif price <= bearish_favour:
            return "Bearish Confirmed"
        elif price <= bearish_value:
            return "Bearish"
        
        today = first_day_prev  # Move one month back
        months_back += 1
        if months_back > 12:  # Limit the search to 1 year max
            return "Neutral"

def calculate_previous_month_high_low(symbol):
    """Calculate the high and low for the previous month."""
    today = datetime.now()
    first_day_of_month = datetime(today.year, today.month, 1)
    last_day_previous_month = first_day_of_month - timedelta(days=1)
    first_day_previous_month = datetime(last_day_previous_month.year, last_day_previous_month.month, 1)

    data = fetch_historical_data(symbol, first_day_previous_month.strftime('%Y-%m-%d'),
                                 last_day_previous_month.strftime('%Y-%m-%d'))
    return data['high'].max(), data['low'].min()


def calculate_current_month_high_low(symbol):
    """Calculate the high and low for the current month."""
    today = datetime.now()
    first_day_of_month = datetime(today.year, today.month, 1)

    data = fetch_historical_data(symbol, first_day_of_month.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
    return data['high'].max(), data['low'].min()


def calculate_previous_week_high_low(symbol):
    """Calculate the high and low for the previous week."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday() + 7)
    end_of_previous_week = start_of_week + timedelta(days=6)

    data = fetch_historical_data(symbol, start_of_week.strftime('%Y-%m-%d'), end_of_previous_week.strftime('%Y-%m-%d'))
    return data['high'].max(), data['low'].min()


def calculate_current_week_high_low(symbol):
    """Calculate the high and low for the current week."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())

    data = fetch_historical_data(symbol, start_of_week.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
    return data['high'].max(), data['low'].min()



def get_thresholds(symbol):
    """Fetch threshold values for a given symbol."""
    category = SYMBOL_MAP.get(symbol.upper())
    if category is None:
        raise ValueError(f"Unknown symbol: {symbol}")
    return THRESHOLD_VALUES[category]

def calculate_thresholds(symbol, pmh, pml):
    """Calculate thresholds for Bullish and Bearish values."""

    thresholds = get_thresholds(symbol)
    a = thresholds["a"]
    b = thresholds["b"]
    

    # print(f"a for {symbol}: {a}")
    # print(f"b for {symbol}: {b}")
    

    bullish_value = pmh + (pmh * a / 100)
    bearish_value = pml - (pml * a / 100)

    bullish_favour = bullish_value + (bullish_value * b / 100)
    bearish_favour = bearish_value - (bearish_value * b / 100)

    return bullish_value, bearish_value, bullish_favour, bearish_favour

def determine_monthly_status(symbol, price, pmh, pml, pwh, pwl, cwh, cwl):
    bullish_value, bearish_value, bullish_favour, bearish_favour = calculate_thresholds(symbol, pmh, pml)

    if price >= bullish_favour:
        return "Bullish Confirmed"
    elif price >= bullish_value:
        return "Bullish"
    elif price <= bearish_favour:
        return "Bearish Confirmed"
    elif price <= bearish_value:
        return "Bearish"

    reversal = check_reversal_conditions(symbol, price, pwh, pwl, cwh, cwl)
    if reversal:
        return reversal

    previous_status = calculate_previous_status(symbol)
    return previous_status

def save_to_csv(symbols):
    data = []
    for symbol in symbols:
        if symbValidator.is_valid_symbol(symbol):
            ltp = fetch_ltp_for_symbol(symbol)
            status = main(symbol, ltp) if ltp is not None else "N/A"
            data.append([symbol, ltp, status])
    
    df = pd.DataFrame(data, columns=["Stock Name", "Last Traded Price", "Current Monthly Status"])
    df.to_csv("stock_status.csv", index=False)
    df.to_excel("stock_status.xlsx", index=False)

def main(symbol, price):
    pmh, pml = calculate_previous_month_high_low(symbol)
    cmh, cml = calculate_current_month_high_low(symbol)
    pwh, pwl = calculate_previous_week_high_low(symbol)
    cwh, cwl = calculate_current_week_high_low(symbol)

    status = determine_monthly_status(symbol, price, pmh, pml, pwh, pwl, cwh, cwl)
    return status
# Example Usage
if __name__ == "__main__":

    # Start the WebSocket connection
    ltp_fetcher.start()

    # Allow some time for the WebSocket to establish connection
    time.sleep(2)

    data = []

    try:
        # Dynamically fetch symbols from SYMBOL_MAP
        symbols = list(SYMBOL_MAP.keys())
        print("Processing the symbols...")
        for symbol in symbols:
            if symbValidator.is_valid_symbol(symbol):
                ltp = fetch_ltp_for_symbol(symbol)
                if ltp is not None:
                    status = main(symbol, ltp) if ltp is not None else "N/A"
                    data.append([symbol, ltp, status])
                else:
                    print(f"LTP for {symbol} not available yet. Please wait...")
            else:
                print(f"symbol {symbol} is invalid")

        df = pd.DataFrame(data, columns=["Stock Name", "Last Traded Price", "Current Monthly Status"])
        print("Writing to CSV file...")
        df.to_csv("stock_status.csv", index=False)
        print("csv Generated successfully")

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        # Stop the WebSocket connection
        ltp_fetcher.stop()   
        
    # Get LTP for "RELIANCE" stock