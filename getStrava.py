import os
import webbrowser
import requests
from stravalib.client import Client
from dotenv import load_dotenv

client = Client()
client.access_token = "your_access_token"

# Get recent activities
activities = client.get_activities(limit=10)
for activity in activities:
    print(activity.name, activity.distance, activity.start_date)