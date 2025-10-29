import os
import webbrowser
import requests
from stravalib.client import Client
from dotenv import load_dotenv
from stravaAuth import get_access_token

load_dotenv()


client = Client()
client.refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
client.access_token = get_access_token()

# Example: get last 5 activities
activities = client.get_activities(limit=5)
for act in activities:
    print(act.name, act.moving_time)