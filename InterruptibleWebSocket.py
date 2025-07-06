import threading
from fyers_apiv3.FyersWebsocket import data_ws


ltp = 0
# Define the callback function for receiving messages
def onmessage(message):
    """
    Callback function to handle incoming messages from the WebSocket.
    This will print the last traded price (LTP) of the symbol.
    """
    if 'ltp' in message:
        ltp=message['ltp']
        print(f"Last Traded Price (LTP) for {message['symbol']}: {message['ltp']}")
        print(f"Last Traded Price (LTP) for {message['symbol']}: {ltp}") 

def onerror(message):
    """
    Callback function to handle WebSocket errors.
    """
    print("Error:", message)

def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)

def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.
    """
    data_type = "SymbolUpdate"
    symbols = ['NSE:SBIN-EQ']  # Replace with the symbol you're interested in
    fyers.subscribe(symbols=symbols, data_type=data_type)

# Replace with your actual access token
access_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3Mzc3OTQyMDksImV4cCI6MTczNzg1MTQ0OSwibmJmIjoxNzM3Nzk0MjA5LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbmxLS2h1eVRJZ3M3V3AtSXV4TzhjLTFZVU1RUUJnRndpcE84OVRJRnpRNnFaOWNmUlU3RmJ5am03Zlh6VGFKZ2NyQVJoSXNuYm43emtmekFORFEtMHVXenF5WE4yX05KYXU3WEc1TnZINHlQRmlvUT0iLCJkaXNwbGF5X25hbWUiOiJNVUtFU0ggS1VNQVIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIzNTI1MjQ3MTdkZjgzNWUxZTRlMDE4MmMzZTEyMGZhZWEyYzUzMTdmYjJlNjEyNGZlMjJmMzdkZCIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWE0zMjg2MyIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.yhd_g9_1Q_aFT5y5CNpeTxqHrsyRMi1_i2q-yaEUGJU'


# Create the FyersDataSocket instance
fyers = data_ws.FyersDataSocket(
    access_token=access_token,  # Access token in the format "appid:accesstoken"
    log_path="",                # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=False,             # Lite mode disabled
    write_to_file=False,        # Don't save logs to file
    reconnect=True,             # Enable auto-reconnection
    on_connect=onopen,          # Callback function for WebSocket connection
    on_close=onclose,           # Callback function for WebSocket close
    on_error=onerror,           # Callback function for WebSocket errors
    on_message=onmessage        # Callback function for WebSocket messages
)

# Function to start the WebSocket in a separate thread
def start_socket():
    print("Starting WebSocket...")
    fyers.connect()

# Function to stop the WebSocket connection
def stop_socket():
    print("Stopping WebSocket...")
    fyers.close_connection()

# Start the WebSocket in a separate thread
socket_thread = threading.Thread(target=start_socket)
socket_thread.start()

# Wait for user input to stop the WebSocket
input("Press Enter to stop the WebSocket...\n")
stop_socket()

# Wait for the socket thread to finish
socket_thread.join()
print("WebSocket stopped.")
