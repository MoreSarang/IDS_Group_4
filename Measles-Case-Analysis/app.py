from io import StringIO
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests 
import plotly.express as px
from utils.data_util import load_data
import re
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Measles-Case-Analysis Dashboard", layout="wide")


def map_region_plot(df):
    # --- Choropleth map prep (total cases by country) ---
    country_cases = df.groupby("country")["measles_total"].sum().reset_index()
    fig = px.choropleth(
        country_cases,
        locations="country",
        locationmode="country names",
        color="measles_total",
        #title="Global Measles Cases by Country (2012–2025)",
        color_continuous_scale="Reds",
        width=1000, height=600
    )
    return fig

def visualize_heatmap(df):
    # ==========================================
    # VISUALIZATION 2: Laboratory Confirmation Rates Heatmap
    # ==========================================
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_aspect('equal')
    # Calculate lab confirmation rates
    df['measles_lab_confirmation_rate'] = np.where(df['measles_total'] > 0,
                                                   df['measles_lab_confirmed'] / df['measles_total'] * 100,
                                                   np.nan)

    # Create pivot table for heatmap
    confirmation_heatmap = df.groupby(['region', 'year'])['measles_lab_confirmation_rate'].mean().unstack()

    sns.heatmap(confirmation_heatmap, annot=True, fmt='.1f', cmap='RdYlBu_r',
            cbar_kws={'label': 'Lab Confirmation Rate (%)'},ax=ax)
    #plt.title('Measles Laboratory Confirmation Rates by Region and Year', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('WHO Region', fontsize=12)   
    return plt

def overall_measles_trend(df):
    # ==========================================
    # VISUALIZATION 1: Global Measles Trends Over Time by Region
    # ==========================================
    plt.figure(figsize=(12, 9))
    plt.subplot(3, 2, 1)

    # Calculate annual totals by region
    annual_measles = df.groupby(['year', 'region'])['measles_total'].sum().unstack(fill_value=0)

    for region in annual_measles.columns:
        plt.plot(annual_measles.index, annual_measles[region],
                marker='o', linewidth=2.5, markersize=6, label=region)

    #plt.title('Global Measles Cases by WHO Region (2012-2025)', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Total Measles Cases', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    return plt

def filter_top_countries(df):
    # --- 2. Sidebar: Top10 toggle + Country selection ---
    st.sidebar.header("Options")
    top10_only = st.sidebar.checkbox("Top 10 countries only", value=False)

    # total cases by country for selection
    country_total = (
        df.groupby("country", as_index=False)["measles_total"]
        .sum()
        .sort_values("measles_total", ascending=False)
    )

    # according to checkbox, limit countries
    if top10_only:
        available_countries = country_total.head(10)["country"].tolist()
    else:
        available_countries = country_total["country"].tolist()

    selected_country = st.sidebar.selectbox("Select a country", available_countries)
    return top10_only, country_total, selected_country
  
def detailed_country_analysis(df,top10_only, country_total, selected_country):
    # --- 4. Country ranking bar chart ---
    col1, col2 = st.columns([1.2, 1.0])

    with col1:
        st.subheader("🏆 Measles Total Cases by Country")
        data = country_total.head(10) if top10_only else country_total
        fig_bar = px.bar(
            data,
            x="country",
            y="measles_total",
            labels={"country": "Country", "measles_total": "Total Cases"},
            title="",
        )
        fig_bar.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader(f"📈 Measles Trend in {selected_country}")
        data = (
            df[df["country"] == selected_country]
            .groupby("year", as_index=False)["measles_total"]
            .sum()
        )
        if not data.empty:
            fig_line = px.bar(
                data,
                x="year",
                y="measles_total",
                labels={"year": "Year", "measles_total": "Total Cases"},
            )
            fig_line.update_layout(height=500)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No data available for this country.")


# ============ Main App ============
def main():
    # App title 
    st.markdown(
        "<h1 style='text-align: center; font-size: 60px; color: Black; font-family: Poppins;'>Measles Case Analysis Dashboard</h1>",
        unsafe_allow_html=True
    )

    # Upload dataset
    csv_data = load_data()


    col1, col2 = st.columns([1.2, 1.0])
    with col1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📈 Global Measles Trends Over Time by Region")
        # add linebreaks
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        fig1 = overall_measles_trend(csv_data)
        st.pyplot(fig1)


    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:0px;'>🗺️ Global Measles Cases by Country (2012–2025)</h3>", unsafe_allow_html=True)
        #st.subheader("🗺️ Global Measles Cases by Country (2012–2025)")
        fig2 = map_region_plot(csv_data)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    top10_only, country_total, selected_country = filter_top_countries(csv_data)
    detailed_country_analysis(csv_data, top10_only, country_total, selected_country)

    st.markdown("---")
    st.subheader("🧪 Measles Laboratory Confirmation Rates by Region and Year")
    fig3 = visualize_heatmap(csv_data)
    st.pyplot(fig3)

if __name__ == "__main__":
    main()
