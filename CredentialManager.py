import json
from fyers_apiv3 import fyersModel
import pandas as pd
from tabulate import tabulate

class CredentialManager:
    def __init__(self, token_file="access_token.json", cred_file="cred.json"):
        self.token_file = token_file
        self.cred_file = cred_file
        self.token_data = {}
        self.config_data = {}
        self.load_access_token()
        self.load_config()
        self.fyers_obj = self.create_fyers_object()

    def load_access_token(self):
        """Load the dynamic access token from its JSON file."""
        try:
            with open(self.token_file, "r") as file:
                self.token_data = json.load(file)
        except Exception as e:
            print(f"❌ Error loading access token: {e}")
            self.token_data = {}

    def load_config(self):
        """Load static credentials from the config JSON file."""
        try:
            with open(self.cred_file, "r") as file:
                self.config_data = json.load(file)
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.config_data = {}           

    def get_access_token(self):
        """Return the current access token."""
        return self.token_data.get("access_token")

    def get_config_value(self, key):
        """Return the static configuration value for a given key."""
        return self.config_data.get(key)

    # You can add dedicated methods for specific keys if desired:
    def get_app_id(self):
        return self.get_config_value("APP_ID")
    
    def get_fyers_id(self):
        return self.get_config_value("FY_ID")   
        
    def get_client_id(self):
        return self.get_config_value("client_id")
    
    def get_totp_object(self):
            """Return the initialized FyersModel object."""
            return self.get_config_value("TOTP_KEY")   
    
    def create_fyers_object(self):
        """
        Instantiate and return a FyersModel object using the loaded credentials.
        Adjust the parameters as required by your FyersModel initialization.
        """
        access_token = self.get_access_token()
        fyers_id = self.get_fyers_id()
        
        if not access_token:
            print("❌ Missing access token! Exiting.")
            exit()
        if not fyers_id:
            print("❌ Missing Fyers App ID! Exiting.")
            exit()
        
        # Create and return the FyersModel object
        #return FyersModel(client_id=fyers_id, token=access_token, log_path="")
        fyers = fyersModel.FyersModel(client_id=fyers_id, token=access_token, log_path="")
        return fyers

    def get_fyers_object(self):
            """Return the initialized FyersModel object."""
            return self.fyers_obj



    # ...and so on for other credentials

# Example usage:
if __name__ == "__main__":
    cred_manager = CredentialManager()
    
    # Access dynamic token
    access_token = cred_manager.get_access_token()
    if not access_token:
        print("❌ Missing access token! Exiting.")
        exit()
    print(f"✅ Access token: {access_token}")
    
    # Access static credentials
    client_id = cred_manager.get_client_id()
    print(f"✅ Client ID: {client_id}")

    credentials = CredentialManager()
    fyers = credentials.get_fyers_object()

    print("✅ FyersModel object initialized and ready to use.")

    data = {
        "symbol": "INFY",
        "resolution": 5,  # Timeframe (5-min, 15-min, etc.)
        "date_format": "1",
        "range_from": "2024-02-01",  # Change to dynamic date logic
        "range_to": "2024-02-12",
        "cont_flag": "1",
    }

    response = fyers.history(data)
    
    if "candles" in response:
        print(f"✅ OHLC Data: {response['candles'][:3]} (Showing 3 candles)")

    else:
        print(f"❌ Error Fetching OHLC: {response}")

