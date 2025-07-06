# fyers_ltp_fetcher.py
import threading
from fyers_apiv3.FyersWebsocket import data_ws

class FyersLTPFetcher:
    def __init__(self, access_token):
        self.access_token = access_token
        self.last_traded_price = None  # Store the LTP
        self.current_symbol = None  # Store the currently tracked symbol
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
        self.subscribed = False  # Track if the WebSocket is subscribed

    def onmessage(self, message):
        """
        Callback to handle incoming WebSocket messages.
        Updates the last traded price (LTP).
        """
        if 'ltp' in message:
            self.last_traded_price = message['ltp']
            self.current_symbol = message['symbol']
            # print(f"LTP Updated: {self.current_symbol} - {self.last_traded_price}")

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
        Dynamically subscribe to a symbol to fetch its LTP.
        """
        if not self.subscribed:
            # print(f"Subscribing to symbol: {symbol}")
            self.fyers.subscribe(symbols=[symbol], data_type="SymbolUpdate")
            self.subscribed = True
        else:
            # print(f"Already subscribed. Switching to symbol: {symbol}")
            self.fyers.unsubscribe(symbols=[self.current_symbol])  # Unsubscribe from the current symbol
            self.fyers.subscribe(symbols=[symbol], data_type="SymbolUpdate")  # Subscribe to the new symbol
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

    def get_ltp(self):
        """
        Return the last traded price.
        """
        return self.last_traded_price
    

