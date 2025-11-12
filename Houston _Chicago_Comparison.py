#!/usr/bin/env python3
# Forecast Houston and Chicago populations to 2050 (exact numbers)
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Load the Excel file
file_path = "Houston - Chicago Comparison.xlsx"
df = pd.read_excel(file_path, sheet_name='Houston-Population-Total-Popula')

# Prepare data
years = df["Year"].values.reshape(-1, 1)
houston_pop = df["Houston Population"].values
chicago_pop = df["Chicago Population"].values

# Train regression models
houston_model = LinearRegression().fit(years, houston_pop)
chicago_model = LinearRegression().fit(years, chicago_pop)

# Predict populations until 2050
future_years = np.arange(df["Year"].min(), 2051).reshape(-1, 1)
houston_forecast = houston_model.predict(future_years)
chicago_forecast = chicago_model.predict(future_years)
