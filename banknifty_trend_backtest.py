import fyers_apiv3  # Import Fyers API V3 (Ensure you have the right credentials)
import pandas as pd
import numpy as np
import credentials as cr
from fyers_apiv3 import fyersModel

client_id = cr.client_id
access_token = cr.access_token
#fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

# Placeholder function to authenticate with Fyers API
def authenticate_fyers():
    # Use your client_id, secret_key, and token
    return fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

# Fetch historical data from Fyers API
# def get_historical_data(fyers, symbol, timeframe, start_date, end_date):
#     data = fyers.history({
#         "symbol": symbol,
#         "resolution": timeframe,
#         "date_format": 1,
#         "range_from": start_date,
#         "range_to": end_date
#     })
    
#     if "candles" not in data:
#         raise ValueError(f"Error fetching data: {data}")  # Handle API errors

#     df = pd.DataFrame(data["candles"], columns=["timestamp", "open", "high", "low", "close", "volume"])
#     df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
#     return df


def get_historical_data(fyers, symbol, start_date, end_date, interval="D"):
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

# Calculate trend confirmation across multiple timeframes
def confirm_trend(df_monthly, df_weekly, df_daily):
    def is_trending(df):
        return df['close'].iloc[-1] > df['close'].rolling(20).mean().iloc[-1]
    
    monthly_trend = is_trending(df_monthly)
    weekly_trend = is_trending(df_weekly)
    daily_trend = is_trending(df_daily)
    
    return (monthly_trend and weekly_trend and daily_trend), (not monthly_trend and not weekly_trend and not daily_trend)

# Identify breakout based on previous day's high/low
def breakout_signal(df_intraday, df_daily):
    prev_high = df_daily['high'].iloc[-1]
    prev_low = df_daily['low'].iloc[-1]
    
    breakout_up = df_intraday[df_intraday['high'] > prev_high]
    breakout_down = df_intraday[df_intraday['low'] < prev_low]
    
    return breakout_up, breakout_down

# Validate with volume and open interest (OI)
def confirm_entry(df_intraday, breakout_df):
    avg_volume = df_intraday['volume'].rolling(20).mean().iloc[-1]
    valid_breakouts = breakout_df[breakout_df['volume'] > 1.5 * avg_volume]
    return not valid_breakouts.empty

# Calculate Profit/Loss
def calculate_pnl(entry_price, exit_price, position_size):
    return (exit_price - entry_price) * position_size

# Main function to backtest strategy
def backtest_strategy(fyers, symbol, start_date, end_date):
    df_monthly = get_historical_data(fyers, symbol, '1M', start_date, end_date)
    df_weekly = get_historical_data(fyers, symbol, '1W', start_date, end_date)
    df_daily = get_historical_data(fyers, symbol, '1D', start_date, end_date)
    df_intraday = get_historical_data(fyers, symbol, '5', start_date, end_date)
    
    bullish_trend, bearish_trend = confirm_trend(df_monthly, df_weekly, df_daily)
    breakout_up, breakout_down = breakout_signal(df_intraday, df_daily)
    
    position_size = 25  # Example: Lot size of Bank Nifty
    
    if bullish_trend and confirm_entry(df_intraday, breakout_up):
        entry_price = breakout_up['high'].iloc[0]
        exit_price = df_intraday['close'].iloc[-1]  # Assuming exit at close
        pnl = calculate_pnl(entry_price, exit_price, position_size)
        print(f"Buy Signal Triggered - P&L: {pnl}")
    elif bearish_trend and confirm_entry(df_intraday, breakout_down):
        entry_price = breakout_down['low'].iloc[0]
        exit_price = df_intraday['close'].iloc[-1]  # Assuming exit at close
        pnl = calculate_pnl(entry_price, exit_price, position_size)
        print(f"Sell Signal Triggered - P&L: {pnl}")
    else:
        print("No Trade Today")

if __name__ == "__main__":
    fyers = authenticate_fyers()
    backtest_strategy(fyers, "NSE:BANKNIFTY", "2024-01-01", "2024-12-31")
