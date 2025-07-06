import requests
from fyers_data import headers, FYERS_BASE_URL

def place_order(symbol, qty, side):
    """ Place Buy/Sell Order """
    url = f"{FYERS_BASE_URL}/orders"
    order = {
        "symbol": symbol,
        "qty": qty,
        "type": 2,
        "side": 1 if side == "BUY" else -1,
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY"
    }
    
    response = requests.post(url, headers=headers, json=order)
    return response.json()

