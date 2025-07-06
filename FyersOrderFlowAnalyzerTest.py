# Replace 'YOUR_ACCESS_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN', and 'YOUR_CHAT_ID' with your actual credentials.
import FyersOrderFlowAnalyzer
import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

if __name__ == "__main__":

    telegram_token = "" #"YOUR_TELEGRAM_BOT_TOKEN"
    chat_id = "247629848" #"YOUR_CHAT_ID"
    symbol = "NSE:RELIANCE-EQ"  # Replace with your desired symbol

    analyzer = FyersOrderFlowAnalyzer(credentials.get_access_token(), telegram_token, chat_id)
    analyzer.start()
    analyzer.subscribe_to_symbol(symbol)

    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        analyzer.stop()
