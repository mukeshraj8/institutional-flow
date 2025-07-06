import time
from fyers_apiv3 import fyersModel
import pandas as pd
from tabulate import tabulate

# Initialize Fyers API
import CredentialManager as cm
credentials = cm.CredentialManager()
fyers = credentials.get_fyers_object()

# ✅ Function to Fetch OHLC Data
def get_ohlc(symbol="NSE:NIFTY50-INDEX", interval="5"):
    data = {
        "symbol": symbol,
        "resolution": interval,  # Timeframe (5-min, 15-min, etc.)
        "date_format": "1",
        "range_from": "2024-02-01",  # Change to dynamic date logic
        "range_to": "2024-02-12",
        "cont_flag": "1",
    }

    response = fyers.history(data)
    
    if "candles" in response:
        print(f"✅ OHLC Data: {response['candles'][:3]} (Showing 3 candles)")
        return response["candles"]
    else:
        print(f"❌ Error Fetching OHLC: {response}")
        return None


# ✅ Function to Fetch Open Interest (OI)
#NSE:SBIN-EQ 
#NSE:BANKNIFTY25FEB49000CE
def get_open_interest_daily_chart(symbol="NSE:SBIN-EQ"):
    #data = {"symbols": symbol}  
    data = {
    "symbol":"NSE:BANKNIFTY25FEB49000CE",
    "ohlcv_flag":"1"
    }
    response = fyers.depth(data)
    print("🔍 Raw API Response:", response)

    if response.get("s") == "ok" and "d" in response:
        oi_value = response["d"][0].get("oi", "N/A")  # Extract OI
        print(f"✅ Open Interest (OI) for {symbol}: {oi_value}")
        return oi_value
    else:
        print(f"❌ Error Fetching OI: {response}")
        return None



# def get_option_chain_v1(symbol="NSE:SBIN-EQ"):
#     #data = {"symbols": symbol}  
#     data = {
#     "symbol":"NSE:TCS-EQ",
#     "strikecount":2,
#     "timestamp": ""
#     }
#     response = fyers.optionchain(data=data);
#     print(response)



import pandas as pd

def get_option_chain(symbol="NSE:TCS-EQ", strikecount=2):
    data = {
        "symbol": symbol,
        "strikecount": strikecount,
        "timestamp": ""
    }
    
    response = fyers.optionchain(data=data)  # Fetch option chain data
    #print("🔍 Raw API Response:", response)  
    
    try:
        if "data" in response and "optionsChain" in response["data"]:
            options = response["data"]["optionsChain"]
            
            oi_data = []
            for option in options:
                strike = option["strike_price"]
                option_type = option["option_type"]
                oi = option.get("oi", "--")  # Open Interest
                oich = option.get("oich", "--")  # OI Change
                oichp = option.get("oichp", "--")  # OI % Change
                volume = option.get("volume", "--")  # Volume

                oi_data.append({
                    "Strike Price": strike,
                    "Type": option_type,
                    "OI": oi,
                    "OI Change": oich,
                    "OI % Change": oichp,
                    "Volume": volume
                })

            # Convert to Pandas DataFrame
            df = pd.DataFrame(oi_data)
            
            # Pivot Table for Better Readability
            df_pivot = df.pivot(index="Strike Price", columns="Type", values=["OI", "OI Change", "OI % Change", "Volume"])
            df_pivot.columns = ['_'.join(col).strip() for col in df_pivot.columns.values]  # Flatten MultiIndex
            df_pivot = df_pivot.reset_index()

            # **Fix Missing Data**: Replace NaN with "--"
            df_pivot = df_pivot.fillna("--")

            # Convert DataFrame to Pretty Table
            
            table = tabulate(df_pivot, headers="keys", tablefmt="pretty")

            print("\n📊 **Formatted Option Chain Data:**")
            print(table)

            return df_pivot

        else:
            print("❌ Error: No OI Data Found in Option Chain")
            return None

    except KeyError:
        print("❌ Error: Unable to extract OI")
        return None


def get_open_interest(symbol="NSE:BANKNIFTY25FEB49000CE"):
    """Fetch Open Interest (OI) from Fyers Option Chain API"""
    data = {
        "symbol": "NSE:BANKNIFTY25FEBFUT",  # Replace with your required index or stock
        "strikecount": 10,  # Fetch strikes around ATM
        "timestamp": ""
    }
    
    response = fyers.optionchain(data=data)

    if response["s"] == "ok" and "data" in response:
        options = response["data"].get("optionsChain", [])

        oi_data = []
        for opt in options:
            strike_price = opt.get("strike_price", "N/A")
            option_type = opt.get("option_type", "N/A")
            oi = opt.get("oi", "N/A")  # If missing, default to N/A
            oich = opt.get("oich", "N/A")  # OI Change
            oichp = opt.get("oichp", "N/A")  # OI % Change
            volume = opt.get("volume", "N/A")

            oi_data.append([strike_price, option_type, oi, oich, oichp, volume])
        
        # Print formatted table
        headers = ["Strike Price", "Type", "OI", "OI Change", "OI % Change", "Volume"]
        print("\n📊 **Live Option Chain Data:**")
        print(tabulate(oi_data, headers=headers, tablefmt="grid"))
    else:
        print(f"❌ Error: Failed to fetch OI Data. Response: {response}")

# Fetch OI every 5 minutes
while True:
    get_ohlc()
    get_open_interest("NSE:BANKNIFTY25FEB49000CE")  # Replace with the option contract you need
    time.sleep(300)  # Wait for 5 minutes


# 🔥 Run Data Fetching
if __name__ == "__main__":

    print("\n📊 Fetching Market Data...\n")
    ohlc_data = get_ohlc()

    print("\n📊 Fetching Option Chain Data...\n")
    #oi_data = get_option_chain()
    #oi_data = get_option_chain()

    oi_data = get_open_interest()
    #get_open_interest_option_chain()

    # if ohlc_data and oi_data:
    #     print("🚀 Data Fetch Successful!")
    # else:
    #     print("❌ Failed to fetch complete data.")






