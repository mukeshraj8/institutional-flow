import requests
import json
import webbrowser
import credentials as cr

# Replace these with your Fyers API credentials
CLIENT_ID = cr.client_id   # App ID from Fyers
SECRET_KEY = cr.secret_key
REDIRECT_URI = 'https://myapi.fyers.in/'
FYERS_API_URL = "https://api.fyers.in/api/v3"
GRANT_TYPE = "authorization_code"

from fyers_apiv3 import fyersModel
# Create a session model with the provided credentials
session = fyersModel.SessionModel(
    client_id=CLIENT_ID,
    secret_key=SECRET_KEY,
    redirect_uri=REDIRECT_URI,
    response_type="code"
)

# Generate the auth code using the session model
response = session.generate_authcode()

# Step 1: Generate the Authorization URL
#auth_url = f"https://api-t1.fyers.in/api/v3/generate-authcode?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&state=None"
auth_url = response

print(f"🔗 Open this URL in a browser and login:\n{auth_url}")
webbrowser.open(auth_url)

# Step 2: Enter the authorization code manually after login
auth_url = input("Enter the Authorization Code: ")

s1=auth_url.split('auth_code=')
auth_code=s1[1].split('&state')[0]

# Step 3: Exchange auth_code for access_token
session = fyersModel.SessionModel(
    client_id=CLIENT_ID,
    secret_key=SECRET_KEY,
    redirect_uri=REDIRECT_URI,
    response_type="code",
    grant_type=GRANT_TYPE
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
token_data = session.generate_token()

if "access_token" in token_data:
    access_token = token_data["access_token"]
    print(f"✅ Access Token Generated: {access_token}")

    # Save token for reuse
    with open("access_token.json", "w") as f:
        json.dump(token_data, f)
else:
    print(f"❌ Error: {token_data}")
