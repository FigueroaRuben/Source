import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Chicago Snow Model
# File: C:/Users/Ruben/OneDrive/Desktop/Source/Chicago Snow.py
# Generates a synthetic daily snowfall series (inches) for Chicago from 2024-11-01 to 2025-03-01,
# saves CSV and a time-series PNG. Reproducible via seed.

import matplotlib.pyplot as plt

# Parameters (tweak as desired)
SEED = 42
np.random.seed(SEED)

START = "2024-11-01"
END = "2025-03-01"
CENTER_DATE = pd.to_datetime("2025-01-15")   # approximate peak of snow season
SIGMA_DAYS = 30.0                            # width of the seasonal snowfall window
BASE_PROB = 0.10                             # baseline daily probability of any snow
PEAK_PROB = 0.75                             # maximum daily probability at season peak
BASE_MEAN_IN = 0.2                           # mean snowfall (inches) when seasonal factor ~= 0
PEAK_MEAN_IN = 4.0                           # mean snowfall (inches) at season peak (conditional on snow)
GAMMA_SHAPE = 2.0                            # gamma shape parameter for positive snowfall amounts

# Create date index
dates = pd.date_range(start=START, end=END, freq="D")
n = len(dates)

# Seasonal factor (0..1) using Gaussian curve around CENTER_DATE
days_from_center = (dates - CENTER_DATE).days.astype(float)
seasonal_factor = np.exp(-0.5 * (days_from_center / SIGMA_DAYS) ** 2)
# Normalize seasonal_factor so max is 1
seasonal_factor /= seasonal_factor.max()

# Daily probability of any snow (clamped 0..1)
p_snow = np.clip(BASE_PROB + (PEAK_PROB - BASE_PROB) * seasonal_factor, 0.0, 1.0)

# Mean snowfall when snow occurs (inches), scales with seasonal factor
mean_when_snow = BASE_MEAN_IN + (PEAK_MEAN_IN - BASE_MEAN_IN) * seasonal_factor

# Simulate snow occurrence and amounts using Gamma for positive amounts
occurs = np.random.rand(n) < p_snow
# Gamma scale parameter = mean / shape
scale = mean_when_snow / GAMMA_SHAPE
positive_amounts = np.random.gamma(shape=GAMMA_SHAPE, scale=scale, size=n)
amounts = np.where(occurs, positive_amounts, 0.0)
# Round to 2 decimal places for readability
amounts = np.round(amounts, 2)

# Build DataFrame
df = pd.DataFrame({
    "date": dates,
    "snow_in": amounts,
    "snow_flag": amounts > 0
})
df.set_index("date", inplace=True)

# Basic summary
summary = {
    "start": START,
    "end": END,
    "days": n,
    "total_snow_inches": float(df["snow_in"].sum()),
    "days_with_snow": int(df["snow_flag"].sum()),
    "mean_daily_snow_when_snow": float(df.loc[df["snow_flag"], "snow_in"].mean() if df["snow_flag"].any() else 0.0)
}
print("Summary:", summary)

# Save CSV
csv_path = "chicago_snowfall_2024-2025.csv"
df.to_csv(csv_path)
print(f"Saved CSV -> {csv_path}")

# Plot time series and save PNG
plt.figure(figsize=(12,4))
plt.bar(df.index, df["snow_in"], color="#1f77b4", width=0.8)
plt.title("Synthetic Daily Snowfall — Chicago (Nov 1, 2024 – Mar 3, 2025)")
plt.ylabel("Snow (inches)")
plt.xlabel("Date")
plt.tight_layout()
png_path = "chicago_snowfall_2024-2025.png"
plt.savefig(png_path, dpi=150)
plt.close()
print(f"Saved plot -> {png_path}")

# If run interactively, you can inspect the first rows:
if __name__ == "__main__":
    print(df.head(15))