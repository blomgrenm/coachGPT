import os
import datetime, time
# import webbrowser
# import requests
from stravalib.client import Client
from dotenv import load_dotenv
from stravaAuth import get_access_token

load_dotenv()

# Example: get last 5 activities
# activities = client.get_activities(limit=5) 
# for act in activities:
#     print(act.name, act.moving_time)


# ==========================
# AUTHENTICATION
# ==========================
def get_strava_client():
    client = Client()
    client.refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
    client.access_token = get_access_token()
    return client


# ==========================
# DATA PROCESSING
# ==========================
def summarize_activity(act, laps):
    """Summarize one activity and its laps for AI processing."""
    laps_data = []
    for lap in laps:
        laps_data.append({
            "lap_dist_km": round(lap.distance.num / 1000, 2) if lap.distance else None,
            "lap_time_min": round(lap.elapsed_time.total_seconds() / 60, 2),
            "avg_hr": getattr(lap, "average_heartrate", None)
        })

    # Sort laps by time for fastest segments
    fastest = sorted(laps_data, key=lambda x: x["lap_time_min"])[:3] if laps_data else []

    summary = {
        "id": act.id,
        "type": act.sport_type,
        "date": act.start_date_local.strftime("%Y-%m-%d"),
        "dist_km": round(act.distance.num / 1000, 2) if act.distance else None,
        "dur_min": round(act.moving_time.total_seconds() / 60, 1),
        "avg_hr": getattr(act, "average_heartrate", None),
        "pace_min_km": round(act.moving_time.total_seconds() / (act.distance.num / 1000) / 60, 2)
                       if act.distance and act.distance.num > 0 else None,
        "fastest_laps": fastest
    }
    return summary


# ==========================
# PERSONAL BESTS
# ==========================
def fetch_personal_bests(client):
    athlete = client.get_athlete()
    stats = client.get_athlete_stats(athlete.id)
    pb_data = {
        "athlete_id": athlete.id,
        "updated": datetime.utcnow().isoformat(),
        "pb_5k": getattr(stats, "best_5k_effort", None),
        "pb_10k": getattr(stats, "best_10k_effort", None),
        "pb_half": getattr(stats, "best_half_marathon_effort", None),
        "pb_marathon": getattr(stats, "best_marathon_effort", None)
    }
    return pb_data

# ==========================
# MAIN LOGIC
# ==========================
def main():
    print("🔗 Connecting to Strava...")
    client = get_strava_client()
    # init_db()

    print("📊 Fetching last 50 activities...")
    activities = client.get_activities(limit=50)
    results = []

    for act in activities:
        if act.sport_type not in ["Run", "Nordic Ski", "Roller Ski"]:
            continue
        try:
            laps = list(client.get_activity_laps(act.id))
        except Exception as e:
            print(f"⚠️ Skipping {act.id} - no laps: {e}")
            laps = []
        summary = summarize_activity(act, laps)
        results.append({"id": act.id, "raw": act.to_dict(), "summary": summary})
        time.sleep(0.4)  # respect rate limit

    print(f"✅ {len(results)} workouts fetched and summarized.")
    # store_training_data(results)

    print("🏅 Fetching personal bests...")
    pb = fetch_personal_bests(client)
    # store_personal_bests(pb)

    # print("✅ Personal bests and workouts stored in SQLite.")


if __name__ == "__main__":
    main()