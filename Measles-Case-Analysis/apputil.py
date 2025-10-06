import pandas as pd
import plotly.express as px
import streamlit as st

# ===========================
# 📊 Measles Visualization Dashboard (Streamlit version)
# ===========================

st.set_page_config(page_title="Measles Dashboard", layout="wide")

# --- 1. Load and clean data ---
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1wgIfOVS2V96_0Jwb6dePuxShpB43FltdLK3k0miyRhE/export?format=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.replace(r"\s+", "_", regex=True).str.strip().str.lower()
    df["country"] = df["country"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    return df

df = load_data()

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

# --- 3. Global Choropleth Map ---
st.subheader("🗺️ Global Measles Cases by Country (2012–2025)")

country_cases = (
    df.groupby("country", as_index=False)["measles_total"]
      .sum()
      .sort_values("measles_total", ascending=False)
)

fig_map = px.choropleth(
    country_cases,
    locations="country",
    locationmode="country names",
    color="measles_total",
    color_continuous_scale="Reds",
    title=None,
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

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
