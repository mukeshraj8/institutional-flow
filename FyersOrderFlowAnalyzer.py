import threading
import json
import requests
from fyers_apiv3.FyersWebsocket import data_ws

class FyersOrderFlowAnalyzer:
    def __init__(self, access_token, telegram_token, chat_id):
        self.access_token = access_token
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.current_symbol = None
        self.subscribed = False
        self.fyers = data_ws.FyersDataSocket(
            access_token=self.access_token,
            log_path="",
            litemode=False,
            write_to_file=False,
            reconnect=True,
            on_connect=self.onopen,
            on_close=self.onclose,
            on_error=self.onerror,
            on_message=self.onmessage
        )

    def onmessage(self, message):
        """
        Callback to handle incoming WebSocket messages.
        Analyzes market depth data for significant order flow changes.
        """
        try:
            data = json.loads(message)
            if 'd' in data:
                market_depth = data['d']
                self.analyze_order_flow(market_depth)
        except json.JSONDecodeError:
            print("Received non-JSON message:", message)

    def analyze_order_flow(self, market_depth):
        """
        Analyzes market depth data to detect large orders and significant spread changes.
        """
        bids = market_depth.get('bids', [])
        asks = market_depth.get('asks', [])

        # Define thresholds
        large_order_threshold = 10000  # Example threshold for large orders
        spread_threshold = 0.5  # 0.5% spread

        # Detect large buy orders
        large_bids = [bid for bid in bids if bid['quantity'] > large_order_threshold]
        if large_bids:
            message = f"📈 Large Buy Orders Detected: {large_bids}"
            print(message)
            self.send_telegram_message(message)

        # Detect large sell orders
        large_asks = [ask for ask in asks if ask['quantity'] > large_order_threshold]
        if large_asks:
            message = f"📉 Large Sell Orders Detected: {large_asks}"
            print(message)
            self.send_telegram_message(message)

        # Calculate bid-ask spread
        if bids and asks:
            best_bid = bids[0]['price']
            best_ask = asks[0]['price']
            spread = ((best_ask - best_bid) / best_bid) * 100
            if spread > spread_threshold:
                message = f"⚠️ Wide Bid-Ask Spread Detected: {spread:.2f}%"
                print(message)
                self.send_telegram_message(message)

    def send_telegram_message(self, message):
        """
        Sends a message to the specified Telegram chat.
        """
        api_url = f'https://api.telegram.org/bot{self.telegram_token}/sendMessage'
        try:
            response = requests.post(api_url, json={'chat_id': self.chat_id, 'text': message})
            if response.status_code != 200:
                print(f"Failed to send message: {response.text}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def onerror(self, message):
        print("Error:", message)

    def onclose(self, message):
        print("Connection closed:", message)

    def onopen(self):
        """
        WebSocket connection opened.
        """
        print("WebSocket connected. Ready to subscribe to symbols.")

    def subscribe_to_symbol(self, symbol):
        """
        Subscribe to a symbol to fetch its market depth data.
        """
        if not self.subscribed:
            print(f"Subscribing to symbol: {symbol}")
            self.fyers.subscribe(symbols=[symbol], data_type="orderBook")
            self.subscribed = True
        else:
            print(f"Already subscribed. Switching to symbol: {symbol}")
            self.fyers.unsubscribe(symbols=[self.current_symbol])  # Unsubscribe from the current symbol
            self.fyers.subscribe(symbols=[symbol], data_type="orderBook")  # Subscribe to the new symbol
        self.current_symbol = symbol

    def start(self):
        """
        Start the WebSocket connection.
        """
        threading.Thread(target=self.fyers.connect).start()

    def stop(self):
        """
        Stop the WebSocket connection.
        """
        print("Stopping WebSocket...")
        self.fyers.close_connection()
