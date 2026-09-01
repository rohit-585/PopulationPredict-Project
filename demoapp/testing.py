import pandas as pd
import os

# Hardcoded path to CSV for quick test
csv_path = r"C:\Users\neera\OneDrive\Desktop\django\mysite\demoapp\static\cleaned_population_data.csv"

df = pd.read_csv(csv_path)
print(df.head())
