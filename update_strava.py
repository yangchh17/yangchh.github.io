"""
update_strava.py
────────────────
Fetches all Snowboard activities from Strava and regenerates
asset/snowboard-runs.geojson used by snowboard.html.

Setup
─────
1. pip install requests python-dotenv
2. Copy .env.example to .env and fill in your Strava credentials.
3. Run: python update_strava.py

To get your credentials:
  - Go to https://www.strava.com/settings/api → note Client ID and Client Secret
  - Get your refresh token via the OAuth flow (see STRAVA_SETUP.md or
    use https://developers.strava.com/docs/getting-started/ for a one-time token)
"""

import json
import math
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
CLIENT_ID     = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

OUTPUT_PATH = Path(__file__).parent / "asset" / "snowboard-runs.geojson"
SPORT_TYPE  = "Snowboard"   # change to "AlpineSki" for skiing


# ── Auth: refresh access token ─────────────────────────────────────────────
def get_access_token():
    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type":    "refresh_token",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── Fetch all activities of given sport type ──────────────────────────────
def fetch_activities(token, sport_type):
    activities = []
    page = 1
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        resp = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        activities.extend(a for a in batch if a.get("sport_type") == sport_type)
        page += 1

    return activities


# ── Fetch streams for a single activity ──────────────────────────────────
def fetch_streams(token, activity_id):
    resp = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}/streams",
        headers={"Authorization": f"Bearer {token}"},
        params={"keys": "latlng,altitude,velocity_smooth,time", "key_by_type": "true"},
    )
    resp.raise_for_status()
    return resp.json()


# ── Build one GeoJSON feature ─────────────────────────────────────────────
def build_feature(activity, streams):
    latlng   = streams.get("latlng",           {}).get("data", [])
    altitude = streams.get("altitude",         {}).get("data", [])
    velocity = streams.get("velocity_smooth",  {}).get("data", [])
    times    = streams.get("time",             {}).get("data", [])

    if not latlng:
        return None

    # Pad altitude/velocity arrays if missing data
    altitude = altitude or [0] * len(latlng)
    velocity = velocity or [0] * len(latlng)

    # Coordinates: [lng, lat, elevation]
    coordinates = [
        [pt[1], pt[0], round(alt, 1)]
        for pt, alt in zip(latlng, altitude)
    ]

    # Speed per point in km/h
    speeds = [round(v * 3.6, 2) for v in velocity]

    # Stats
    speeds_nonzero = [s for s in speeds if s > 0]
    max_speed_kmh = round(max(speeds_nonzero), 2) if speeds_nonzero else 0
    avg_speed_kmh = round(sum(speeds_nonzero) / len(speeds_nonzero), 2) if speeds_nonzero else 0

    # Accumulated vertical descent (sum of all downhill segments)
    vert_m = 0.0
    for i in range(1, len(altitude)):
        drop = altitude[i - 1] - altitude[i]
        if drop > 0:
            vert_m += drop
    vert_m = round(vert_m, 1)

    distance_km = round(activity["distance"] / 1000, 3)
    duration_min = round(activity["moving_time"] / 60, 2)

    # Date string "YYYY-MM-DD"
    date_str = activity["start_date_local"][:10]

    # Resort: use activity name (rename your Strava activity to the resort name)
    # Or use activity["location_city"] if Strava fills that in for you
    resort = activity.get("name", "Unknown Resort")

    activity_id = str(activity["id"])

    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates,
        },
        "properties": {
            "id":            f"{date_str} - {resort}",
            "date":          date_str,
            "resort":        resort,
            "distance_km":   distance_km,
            "vert_m":        vert_m,
            "max_speed_kmh": max_speed_kmh,
            "avg_speed_kmh": avg_speed_kmh,
            "duration_min":  duration_min,
            "speeds":        speeds,
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        raise SystemExit(
            "Missing credentials. Copy .env.example to .env and fill in "
            "STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN."
        )

    print("Refreshing Strava access token...")
    token = get_access_token()

    print(f"Fetching {SPORT_TYPE} activities...")
    activities = fetch_activities(token, SPORT_TYPE)
    print(f"  Found {len(activities)} activities")

    features = []
    for i, activity in enumerate(activities, 1):
        name = activity.get("name", activity["id"])
        print(f"  [{i}/{len(activities)}] {activity['start_date_local'][:10]} — {name}")
        try:
            streams = fetch_streams(token, activity["id"])
            feature = build_feature(activity, streams)
            if feature:
                features.append(feature)
        except Exception as e:
            print(f"    Warning: skipped ({e})")

    # Sort newest first (matches current file order)
    features.sort(key=lambda f: f["properties"]["date"], reverse=True)

    geojson = {"type": "FeatureCollection", "features": features}

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(geojson, f, separators=(",", ":"))

    print(f"\nWrote {len(features)} features → {OUTPUT_PATH}")
    print("Run deploy.bat to push to GitHub.")


if __name__ == "__main__":
    main()
