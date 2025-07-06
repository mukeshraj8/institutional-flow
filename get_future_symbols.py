import requests

def get_fyers_symbols(access_token, market="NSE_FO"):
    """
    Fetch all symbols from the FYERS API for the given market segment.
    
    :param access_token: Your FYERS access token
    :param market: Market segment (e.g., 'NSE_FO' for futures and options)
    :return: List of symbols in the specified market
    """
    url = "https://api.fyers.in/api/v2/symbol_list"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "exchange": market
    }

    response = requests.get(url, headers=headers, params=payload)

    if response.status_code == 200:
        data = response.json()
        if data["code"] == 200:
            symbols = data.get("data", [])
            futures_symbols = [s for s in symbols if "FUT" in s["symbol"]]
            return futures_symbols
        else:
            raise Exception(f"API Error: {data.get('message', 'Unknown Error')}")
    else:
        raise Exception(f"HTTP Error: {response.status_code}")

# Example usage
import CredentialManager as cm
credentials = cm.CredentialManager()
access_token = credentials.get_access_token()
#access_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3Mzc3OTQyMDksImV4cCI6MTczNzg1MTQ0OSwibmJmIjoxNzM3Nzk0MjA5LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbmxLS2h1eVRJZ3M3V3AtSXV4TzhjLTFZVU1RUUJnRndpcE84OVRJRnpRNnFaOWNmUlU3RmJ5am03Zlh6VGFKZ2NyQVJoSXNuYm43emtmekFORFEtMHVXenF5WE4yX05KYXU3WEc1TnZINHlQRmlvUT0iLCJkaXNwbGF5X25hbWUiOiJNVUtFU0ggS1VNQVIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIzNTI1MjQ3MTdkZjgzNWUxZTRlMDE4MmMzZTEyMGZhZWEyYzUzMTdmYjJlNjEyNGZlMjJmMzdkZCIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWE0zMjg2MyIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.yhd_g9_1Q_aFT5y5CNpeTxqHrsyRMi1_i2q-yaEUGJU'
try:
    futures_symbols = get_fyers_symbols(access_token)
    print("Futures Symbols:", [s["symbol"] for s in futures_symbols])
except Exception as e:
    print(f"Error: {e}")
