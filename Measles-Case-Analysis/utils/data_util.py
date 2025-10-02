import pandas as pd

def load_data():
    """Load CSV into DataFrame"""
    return pd.read_csv("https://docs.google.com/spreadsheets/d/1NDwpwpJ2arnsmbZdwJIIxIUnt4rxd8px257JhOSXc7c/export?format=csv")

