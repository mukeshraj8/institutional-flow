import websocket
import json
import requests
import time
from fyers_apiv3 import fyersModel
import credentials as cr

# ✅ Load Access Token
def load_access_token():
    try:
        with open("access_token.json", "r") as file:
            data = json.load(file)
            return data.get("access_token")
    except Exception as e:
        print(f"❌ Error loading access token: {e}")
        return None

# ✅ Initialize FYERS API
access_token = load_access_token()
if not access_token:
    print("❌ Missing access token! Exiting.")
    exit()

fyers = fyersModel.FyersModel(client_id=cr.FY_ID, is_async=False, token=access_token)

SYMBOL = "NSE:RELIANCE-EQ"
WS_URL = "wss://api.fyers.in/socket/v2"
API_URL = "https://api.fyers.in/api/v2/market_depth"

# Thresholds for detecting institutional activity
LARGE_ORDER_THRESHOLD = 10000  # Orders greater than 10,000 shares
SPREAD_THRESHOLD = 0.5  # If bid-ask spread exceeds 0.5%

# Fetch Market Depth via REST API
def fetch_market_depth():
    response = requests.post(API_URL, json={"symbol": SYMBOL, "depth": 5}, headers={"Authorization": f"Bearer {access_token}"})
    return response.json()

# Analyze Order Flow for Large Orders and Imbalances
def analyze_order_flow(data):
    bids = data.get("bids", [])
    asks = data.get("asks", [])
    
    large_bids = [bid for bid in bids if bid["quantity"] > LARGE_ORDER_THRESHOLD]
    large_asks = [ask for ask in asks if ask["quantity"] > LARGE_ORDER_THRESHOLD]
    
    if large_bids:
        print(f"📈 Institutional Buying Detected: {large_bids}")
    if large_asks:
        print(f"📉 Institutional Selling Detected: {large_asks}")
    
    if bids and asks:
        spread = (asks[0]["price"] - bids[0]["price"]) / bids[0]["price"] * 100
        if spread > SPREAD_THRESHOLD:
            print(f"⚠️ Wide Bid-Ask Spread Detected: {spread:.2f}%")

# WebSocket Callbacks
def on_message(ws, message):
    data = json.loads(message)
    analyze_order_flow(data)

def on_open(ws):
    payload = json.dumps({"symbol": [SYMBOL], "depth": 5})
    ws.send(payload)
    print("🔗 Connected to FYERS WebSocket...")

def start_websocket():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_open=on_open)
    ws.run_forever()

if __name__ == "__main__":
    print("🚀 Starting Order Flow Analysis Bot...")
    start_websocket()
