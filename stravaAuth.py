import os
import requests
from dotenv import load_dotenv

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")


def get_access_token():
    """Refresh the Strava access token using the long-lived refresh token."""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": STRAVA_REFRESH_TOKEN,
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")

    token_data = response.json()
    access_token = token_data["access_token"]

    # Optional: Update refresh token if it changes (rare)
    new_refresh_token = token_data.get("refresh_token")
    if new_refresh_token and new_refresh_token != STRAVA_REFRESH_TOKEN:
        update_env_file("STRAVA_REFRESH_TOKEN", new_refresh_token)

    return access_token


def update_env_file(key, value):
    """Update a key-value pair in .env file."""
    lines = []
    with open(".env", "r") as file:
        lines = file.readlines()

    with open(".env", "w") as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
            else:
                file.write(line)


if __name__ == "__main__":
    print("Access token:", get_access_token())
