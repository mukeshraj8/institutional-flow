import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

def is_valid_symbol(symbol):
    # API call to get symbol details
    data = {
        "symbols": f"{symbol}"
    }

    try:
        #print(f"input Symbol Received is : {data}")
        response = fyers.quotes(data=data)
        #print(response)
        
        # Parsing the response
        if response.get("s") == "ok" and response.get("d"):
            v_data = response["d"][0].get("v", {})

            if v_data.get("s") == "error":
                return False  # Invalid symbol
            else:
                return True   # Valid symbol
        else:
            return False  # Invalid structure or missing data
 
    except Exception as e:
        print(f"Error: {e}")
        return False

# Main Execution Function
def main(symbol, price):

    status = "True"
    return status   


# Example Usage
if __name__ == "__main__":

    try:
        # Example: Fetch LTP for specific symbols
        symbols = ["NSE:SBIN-EQ", "NSE:RELIANCE-EQ", "NSE:INFY-EQ", "NSE:DGCONTENT-BE","NSE:NIFTY50-INDEX"]
        # Dynamically fetch symbols from SYMBOL_MAP
        #for symbol in symbols:

        symbol="NSE:SBIN-EB"
        if is_valid_symbol(symbol):
            print(f"The symbol '{symbol}' is valid in Fyers Equity Segment.")

        else:
            print(f"The symbol '{symbol}' is NOT valid in Fyers Equity Segment.")

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        # Stop the WebSocket connection
        print("Application Stopped...") 
        
