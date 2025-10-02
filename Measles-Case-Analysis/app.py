from io import StringIO
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests 
import plotly.express as px
from utils.data_util import load_data
import re
import warnings
warnings.filterwarnings('ignore')


def map_region_plot(df):
    
    # --- Time-series trend of global measles cases ---
    yearly_cases = df.groupby("year")["measles_total"].sum().reset_index()

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=yearly_cases, x="year", y="measles_total", marker="o")
    plt.title("Global Measles Cases (2012–2025)")
    plt.xlabel("Year")
    plt.ylabel("Total Cases")
    plt.grid(True)
    plt.show()

    # --- Choropleth map prep (total cases by country) ---
    country_cases = df.groupby("country")["measles_total"].sum().reset_index()

    fig = px.choropleth(
        country_cases,
        locations="country",
        locationmode="country names",
        color="measles_total",
        title="Global Measles Cases by Country (2012–2025)",
        color_continuous_scale="Reds"
    )
    return fig


# ============ Main App ============
def main():
    # App title 
    st.title("📊 Measles Cases Dashboard")

    # Upload dataset
    csv_data = load_data()
    st.markdown("### Global Measles Cases Data (2012–2025)")
    fig = map_region_plot(csv_data)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
