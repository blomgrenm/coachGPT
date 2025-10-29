from dotenv import load_dotenv
import os
import requests  # or httpx, depending on your setup

load_dotenv()

# Access them with os.getenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("CLIENT_REFRESH_TOKEN")

def get_token(client_id, client_secret,refresh_token):
    url = "https://www.strava.com/api/v3/oauth/token"  # your token endpoint
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, data=data)
    response.raise_for_status()  # raises an error if not 200
    token = response.json().get("access_token")

    return token