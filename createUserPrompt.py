# createUserPrompt.py
import sqlite3, json, gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

DB_PATH = "training.db"

def read_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    return data[0]  # assuming background and goals are on first row

def get_recent_training():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT summary_json FROM training_data ORDER BY created_at DESC LIMIT 20")
    data = [json.loads(x[0]) for x in c.fetchall()]
    conn.close()
    return data

def build_prompt(sheet_data, training_data):
    prompt = f"""
User Background:
- Experience: {sheet_data['experience']}
- Weekly Volume: {sheet_data['weekly_volume_km']} km
- Goal: {sheet_data['goal']}
- Target Race: {sheet_data['target_race']} ({sheet_data['race_date']})

Recent Workouts Summary (JSON schema: id, sport_type, distance_km, duration_min, avg_hr, laps):
{json.dumps(training_data, indent=2)}

Please create a personalized running plan that starts from today and leads to the goal above. 
Provide a weekly overview with day-by-day training recommendations, intervals, rest days, and target efforts.
"""
    return prompt

if __name__ == "__main__":
    sheet_data = read_google_sheet("Running Goals")
    training_data = get_recent_training()
    user_prompt = build_prompt(sheet_data, training_data)
    with open("user_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_prompt)
