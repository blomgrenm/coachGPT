import os
# from datetime import datetime, timezone, timedelta
import time
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
    client.token_expires = time.time() + 21600 # Expires in 6 hours
    client.access_token = get_access_token()
    return client


# ==========================
# DATA PROCESSING
# ==========================
def summarize_activity(act, laps):
    """Summarize one activity and its laps for AI processing."""

    def to_km(distance_obj):
            """Convert Strava Distance object to km safely."""
            if not distance_obj:
                return None
            try:
                return round(float(distance_obj) / 1000, 2)
            except Exception:
                return None
            
    def to_minutes(duration_obj):
        """Convert Strava Duration or timedelta to minutes safely."""
        if not duration_obj:
            return None
        try:
            return round(float(duration_obj) / 60, 2)
        except Exception:
            # Fallback for timedelta
            return round(duration_obj.total_seconds() / 60, 2)

    laps_data = []
    for lap in laps:
        laps_data.append({
            "lap_dist_km": to_km(getattr(lap, "distance", None)),
            "lap_time_min": to_minutes(getattr(lap, "elapsed_time", None)),
            "avg_hr": getattr(lap, "average_heartrate", None)
        })

    # Sort laps by time for fastest segments
    fastest = sorted(laps_data, key=lambda x: x["lap_time_min"])[:3] if laps_data else []

    # Compute overall metrics
    dist_km = to_km(getattr(act, "distance", None))
    dur_min = to_minutes(getattr(act, "moving_time", None))
    avg_hr = getattr(act, "average_heartrate", None)
    pace_min_km = round(dur_min / dist_km, 2) if dist_km and dur_min else None

    summary = {
        "id": act.id,
        "type": act.sport_type,
        "date": act.start_date_local.strftime("%Y-%m-%d"),
        "dist_km": dist_km,
        "dur_min": dur_min,
        "avg_hr": avg_hr,
        "pace_min_km": pace_min_km,
        "fastest_laps": fastest
    }
    return summary


# ==========================
# PERSONAL BESTS
# ==========================
# def fetch_personal_bests(client):
#     athlete = client.get_athlete()
#     stats = client.get_athlete_stats(athlete.id)
#     print(vars(stats))
#     pb_data = {
#         "athlete_id": athlete.id,
#         "updated": datetime.now(timezone.utc).isoformat(),
#         "pb_5k": getattr(stats, "best_5k_effort", None),
#         "pb_10k": getattr(stats, "best_10k_effort", None),
#         "pb_half": getattr(stats, "best_half_marathon_effort", None),
#         "pb_marathon": getattr(stats, "best_marathon_effort", None)
#     }
#     return pb_data

# ==========================
# MAIN LOGIC
# ==========================
def main():
    print("🔗 Connecting to Strava...")
    client = get_strava_client()
    # init_db()

    print("📊 Fetching last 50 activities...")
    activities = client.get_activities(limit=5)
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
        results.append({    
            "id": act.id,
            "raw": {
                "id": act.id,
                "name": act.name,
                "type": act.sport_type,
                "start_date": str(act.start_date_local),
                "distance_m": float(act.distance) if act.distance else None,
                "moving_time_s": float(act.moving_time) if act.moving_time else None,
                "avg_hr": getattr(act, "average_heartrate", None),
                "total_elevation_gain": getattr(act, "total_elevation_gain", None)
            },
            "summary": summary
            })
        time.sleep(0.4)  # respect rate limit

    print(f"✅ {len(results)} workouts fetched and summarized.")
    # store_training_data(results)

    # print("🏅 Fetching personal bests...")
    # pb = fetch_personal_bests(client)
    # for pb_stat in pb:
    #     print(pb_stat,pb[pb_stat])
    # store_personal_bests(pb)

    # print("✅ Personal bests and workouts stored in SQLite.")


if __name__ == "__main__":
    main()