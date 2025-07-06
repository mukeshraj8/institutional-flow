from fyers_apiv3 import fyersModel
import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

# ✅ Request Live OHLC Data
def fetch_live_ohlc(symbol):
    data = {
        "symbols": symbol
    }
    try:
        response = fyers.quotes(data=data)
        print("API Response:", response)  # Debugging line to inspect the response
        
        if response.get("s") == "ok" and "d" in response:
            try:
                ohlc_data = response["d"][0]["v"]  # OHLC data is inside the 'v' key
                
                # Extract values with correct keys
                return {
                    "Open": ohlc_data.get("open_price"),
                    "High": ohlc_data.get("high_price"),
                    "Low": ohlc_data.get("low_price"),
                    "Close": ohlc_data.get("prev_close_price"),  # Adjust as per your requirement
                    "Last Price": ohlc_data.get("lp"),
                    "Volume": ohlc_data.get("volume")
                }
                    
            except (IndexError, KeyError) as e:
                print(f"⚠️ Data format error: {e}")
                print(f"Response received: {response}")
                return None
        else:
            print(f"⚠️ Failed to fetch OHLC data: {response}")
            return None
    
    except Exception as e:
        print(f"⚠️ Exception occurred while fetching data: {e}")
        return None


# ✅ Example Usage
symbol = "NSE:NIFTY25FEBFUT"
ohlc = fetch_live_ohlc(symbol)

if ohlc:
    print("Fetched OHLC Data:", ohlc)
else:
    print("Failed to fetch live OHLC data.")
