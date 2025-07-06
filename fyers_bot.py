import time
from fyers_strategy import check_trade_condition, get_ohlc, get_open_interest
from fyers_order import place_order

# Bot Settings
SYMBOL = "NSE:NIFTY50-INDEX"
QUANTITY = 50
INTERVAL = 300  # Check market conditions every 5 minutes

while True:
    print("🔄 Checking market conditions...")
    
    data = get_ohlc()
    oi_data = get_open_interest()
    trade_signal = check_trade_condition(data, oi_data)
    
    if trade_signal in ["BUY", "SELL"]:
        print(f"🚀 Trade Signal: {trade_signal} | Placing Order...")
        response = place_order(SYMBOL, QUANTITY, trade_signal)
        print(f"✅ Order Response: {response}")
    
    else:
        print("⏳ No trade signal. Waiting for next check...")
    
    time.sleep(INTERVAL)  # Wait for next cycle
