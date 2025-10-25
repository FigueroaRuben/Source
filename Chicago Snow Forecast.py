#!/usr/bin/env python3
"""
Determine whether it will snow in Chicago in the next five days using the NWS API.
Saves no state and requires no API key. Uses Chicago coordinates (41.8781, -87.6298).
"""

import sys
import re
import json
from datetime import datetime, timedelta, timezone
try:
    import requests
except Exception:
    sys.exit("Requires the 'requests' package. Install with: pip install requests")

CHICAGO_LAT = 41.8781
CHICAGO_LON = -87.6298
HEADERS = {"User-Agent": "GitHub Copilot - nws-snow-check@example.com"}
SNOW_KEYWORDS = re.compile(r"\b(snow|sleet|flurries|blizzard|wintry|snowshowers|snow showers|wintry mix)\b", re.I)


def iso_to_dt(iso):
    # datetime.fromisoformat handles offsets like -05:00 and Z (Py3.11+ for 'Z'); handle trailing Z manually
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    return datetime.fromisoformat(iso)


def fetch_json(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def get_forecast_url(lat, lon):
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    data = fetch_json(points_url)
    return data["properties"]["forecast"]


def will_snow_in_next_days(forecast_url, days=5):
    data = fetch_json(forecast_url)
    periods = data.get("properties", {}).get("periods", [])
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)

    snow_periods = []
    for p in periods:
        start_iso = p.get("startTime")
        if not start_iso:
            continue
        start_dt = iso_to_dt(start_iso)
        # convert to aware UTC if not already offset-aware
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if start_dt > cutoff:
            continue
        text = " ".join(filter(None, [p.get("shortForecast", ""), p.get("detailedForecast", "")]))
        if SNOW_KEYWORDS.search(text):
            snow_periods.append({
                "name": p.get("name"),
                "startTime": start_dt.isoformat(),
                "shortForecast": p.get("shortForecast"),
                "detailedForecast": p.get("detailedForecast"),
            })
    return snow_periods


def main():
    try:
        forecast_url = get_forecast_url(CHICAGO_LAT, CHICAGO_LON)
    except Exception as e:
        sys.exit(f"Failed to get forecast endpoint: {e}")

    try:
        snow_periods = will_snow_in_next_days(forecast_url, days=5)
    except Exception as e:
        sys.exit(f"Failed to fetch forecast: {e}")

    result = {
        "location": {"city": "Chicago", "lat": CHICAGO_LAT, "lon": CHICAGO_LON},
        "check_window_days": 5,
        "will_snow": bool(snow_periods),
        "periods": snow_periods,
    }
    # Print JSON so the output is easy to parse by other tools
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()