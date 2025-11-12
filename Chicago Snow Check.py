import requests
import creds
import schedule
import time
from datetime import datetime
import pytz

# Configuration
# Your OpenWeatherMap API key
LAT = 41.8781  # Chicago latitude
LON = -87.6298  # Chicago longitude
TIMEZONE = pytz.timezone('America/Chicago')

def check_snow_today():
    """
    Fetches the 5-day forecast and checks if snow is expected today in Chicago.
    Snow detection: Any weather code 600-622 in today's forecast periods.
    """
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={creds.API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses
        data = response.json()
        
        # Get today's date in Chicago timezone
        today = datetime.now(TIMEZONE).date()
        
        snow_expected = False
        for item in data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'], tz=TIMEZONE)
            if forecast_time.date() == today:
                for weather in item['weather']:
                    if 600 <= weather['id'] <= 622:  # Snow codes: light/heavy snow, snow showers, etc.
                        snow_expected = True
                        break
                if snow_expected:
                    break
        
        if snow_expected:
            print(f"❄️ ALERT: Snow is expected in Chicago today ({today})! Bundle up.")
        else:
            print(f"☀️ No snow expected in Chicago today ({today}). Clear(ish) skies ahead.")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
    except KeyError:
        print("Invalid API response. Check your API key.")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Schedule the job to run daily at 6:00 AM CST
schedule.every().day.at("06:00").do(check_snow_today)

# Main loop to keep the scheduler running
print("Snow checker started. Waiting for 6:00 AM CST...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute