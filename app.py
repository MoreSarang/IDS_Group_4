# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

from apputil import load_data_via_uploader  # local import

st.set_page_config(page_title="Measles/Rubella Dashboard", layout="wide")

# Header
st.markdown("<h1 style='text-align:center; font-size:44px;'>Measles & Rubella Interactive Dashboard</h1>", unsafe_allow_html=True)

# Load data via uploader (no hardcoded paths)
base_wide, base_long = load_data_via_uploader()

# Sidebar filters
st.sidebar.header("Filters")
disease_options = ["Measles","Rubella","Both"]
if {"Measles_per100k","Rubella_per100k"}.issubset(set(base_long["disease"].unique())):
    disease_options += ["Measles_per100k","Rubella_per100k"]
disease_sel = st.sidebar.selectbox("Disease metric", disease_options, index=0)

years_all = sorted([int(y) for y in base_long["year"].dropna().unique().tolist()])
yr_min, yr_max = (years_all[0], years_all[-1]) if years_all else (2012, 2025)
year_range = st.sidebar.slider("Year range", min_value=int(yr_min), max_value=int(yr_max), value=(int(yr_min), int(yr_max)), step=1)

regions = sorted(base_long["region"].dropna().unique().tolist())
regions_sel = st.sidebar.multiselect("Regions", regions, default=regions)

top_n = st.sidebar.number_input("Top N countries", min_value=5, max_value=50, value=10, step=1)
roll_window = st.sidebar.select_slider("Rolling window (years)", options=[1,3,5], value=3)
show_yoy = st.sidebar.checkbox("Show YoY growth", value=True)

# Helpers
def apply_filters(long_df, disease_sel, regions, year_range):
    df = long_df.copy()
    if disease_sel == "Both":
        df = df[df["disease"].isin(["Measles","Rubella"])]
    else:
        df = df[df["disease"] == disease_sel]
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    if regions:
        df = df[df["region"].isin(regions)]
    return df

def fmt_pct(x):
    return "—" if pd.isna(x) else f"{x*100:.1f}%"

long_f = apply_filters(base_long, disease_sel, regions_sel, year_range)

# Preview
with st.expander("Preview data (first 10 rows)"):
    st.dataframe(base_wide.head(10))

# KPI section
kcol1, kcol2, kcol3, kcol4 = st.columns(4)
tot_period = long_f["value"].sum() if not long_f.empty else 0
latest_year = int(long_f["year"].max()) if not long_f.empty else None
latest_total = long_f[long_f["year"]==latest_year]["value"].sum() if latest_year else 0
prev_total = long_f[long_f["year"]==latest_year-1]["value"].sum() if latest_year and (latest_year-1) in long_f["year"].unique() else np.nan
yoy_latest = (latest_total/prev_total-1) if prev_total and prev_total>0 else np.nan
with kcol1: st.metric("Total (filtered period)", f"{int(tot_period):,}")
with kcol2: st.metric(f"Total in {latest_year if latest_year else '—'}", f"{int(latest_total):,}" if latest_year else "—")
with kcol3: st.metric("YoY latest", fmt_pct(yoy_latest))
with kcol4: st.metric("Countries", f"{long_f['country'].nunique():,}")

st.markdown("---")

# Global trend (vertical section)
st.subheader("Global trend over time")
global_agg = (long_f.groupby(["disease","year"], as_index=False)["value"].sum().sort_values("year"))
if not global_agg.empty:
    if disease_sel == "Both":
        g = global_agg.groupby("year", as_index=False)["value"].sum()
        g["rolling"] = g["value"].rolling(roll_window, min_periods=1).mean()
        g["yoy"] = g["value"].pct_change()
        title = "Global totals (Measles + Rubella)"
    else:
        g = global_agg[global_agg["disease"]==disease_sel][["year","value"]].copy()
        g["rolling"] = g["value"].rolling(roll_window, min_periods=1).mean()
        g["yoy"] = g["value"].pct_change()
        title = f"Global totals ({disease_sel})"
    fig_global = go.Figure()
    fig_global.add_trace(go.Bar(x=g["year"], y=g["value"], name="Annual total", marker_color="#cfd8dc"))
    if roll_window > 1:
        fig_global.add_trace(go.Scatter(x=g["year"], y=g["rolling"], name=f"Rolling avg ({roll_window}y)", mode="lines+markers",
                                        line=dict(color="#d32f2f", width=3)))
    if show_yoy:
        fig_global.add_trace(go.Scatter(x=g["year"], y=g["yoy"], name="YoY", mode="lines+markers",
                                        line=dict(color="#1976d2", width=2, dash="dash"), yaxis="y2"))
        fig_global.update_layout(yaxis2=dict(title="YoY", overlaying="y", side="right", tickformat=".0%"))
    fig_global.update_layout(title=title, height=420, margin=dict(l=20,r=20,t=40,b=10), yaxis=dict(title="Cases"))
    st.plotly_chart(fig_global, use_container_width=True)
else:
    st.info("No data for selected filters.")

# Regional trends (vertical section)
st.subheader("Regional trends")
reg_agg = (long_f.groupby(["region","year"], as_index=False)["value"].sum().sort_values(["region","year"]))
if not reg_agg.empty:
    reg_agg["rolling"] = reg_agg.groupby("region")["value"].transform(lambda s: s.rolling(roll_window, min_periods=1).mean())
    fig_reg = px.line(reg_agg, x="year", y="value", color="region", markers=True,
                      labels={"value":"Cases","year":"Year","region":"Region"})
    for reg in reg_agg["region"].unique():
        dreg = reg_agg[reg_agg["region"]==reg]
        fig_reg.add_trace(go.Scatter(x=dreg["year"], y=dreg["rolling"], name=f"{reg} (roll)",
                                     mode="lines", line=dict(width=2, dash="dot"), showlegend=False))
    fig_reg.update_layout(height=420, margin=dict(l=20,r=20,t=10,b=10))
    st.plotly_chart(fig_reg, use_container_width=True)
else:
    st.info("No regional data for selected filters.")

# Choropleth map (vertical section)
st.subheader("Choropleth map")
map_year = st.slider("Select map year", min_value=year_range[0], max_value=year_range[1], value=year_range[1], step=1)
map_df = long_f[long_f["year"]==map_year].groupby("country", as_index=False)["value"].sum()
if not map_df.empty:
    fig_map = px.choropleth(
        map_df, locations="country", locationmode="country names",
        color="value", color_continuous_scale="Reds",
        hover_name="country", hover_data={"value":":,.0f"},
        title=f"{disease_sel if disease_sel!='Both' else 'Measles + Rubella'} — {map_year}"
    )
    fig_map.update_layout(height=520, margin=dict(l=20,r=20,t=50,b=10))
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("No data for selected map year.")

# Country ranking (vertical section)
st.subheader("Country ranking")
rank_df = (long_f.groupby("country", as_index=False)["value"].sum().sort_values("value", ascending=False))
show_top = rank_df.head(int(top_n))
fig_bar = px.bar(show_top, x="country", y="value", labels={"value":"Total (period)"},
                 title=f"Top {min(int(top_n), len(show_top))} countries")
fig_bar.update_layout(height=480, xaxis_tickangle=-45, margin=dict(l=20,r=20,t=50,b=10))
st.plotly_chart(fig_bar, use_container_width=True)

# Country trend (vertical section)
st.subheader("Country trend")
sel_cty = st.selectbox("Select a country", rank_df["country"].tolist() if not rank_df.empty else [])
if sel_cty:
    cty_ts = (long_f[long_f["country"]==sel_cty].groupby("year", as_index=False)["value"].sum().sort_values("year"))
    cty_ts["rolling"] = cty_ts["value"].rolling(roll_window, min_periods=1).mean()
    cty_ts["yoy"] = cty_ts["value"].pct_change()
    fig_cty = go.Figure()
    fig_cty.add_trace(go.Bar(x=cty_ts["year"], y=cty_ts["value"], name="Annual"))
    fig_cty.add_trace(go.Scatter(x=cty_ts["year"], y=cty_ts["rolling"], name=f"Rolling ({roll_window}y)",
                                 line=dict(color="#d32f2f")))
    if show_yoy:
        fig_cty.add_trace(go.Scatter(x=cty_ts["year"], y=cty_ts["yoy"], name="YoY", yaxis="y2",
                                     line=dict(color="#1976d2", dash="dash")))
        fig_cty.update_layout(yaxis2=dict(title="YoY", overlaying="y", side="right", tickformat=".0%"))
    fig_cty.update_layout(height=480, margin=dict(l=20,r=20,t=10,b=10), yaxis=dict(title="Cases"))
    st.plotly_chart(fig_cty, use_container_width=True)

# Heatmap (vertical section)
st.subheader("Heatmap: average measles by region-year")
if "measles" in base_wide.columns:
    heat = (base_wide[(base_wide["year"]>=year_range[0]) & (base_wide["year"]<=year_range[1])]
            .groupby(["region","year"])["measles"].mean().unstack())
    fig_h, ax = plt.subplots(figsize=(12, 4))
    ax.set_aspect('auto')
    sns.heatmap(heat, annot=True, fmt=".1f", cmap="RdYlBu_r",
                cbar_kws={"label":"Avg Measles Cases"})
    ax.set_xlabel("Year"); ax.set_ylabel("Region")
    st.pyplot(fig_h)
else:
    st.info("Measles field not available for heatmap in the uploaded file.")

# Download (vertical section)
st.subheader("Download filtered data")
if not long_f.empty:
    st.download_button(
        "Download CSV",
        data=long_f.sort_values(["country","region","disease","year"]).to_csv(index=False).encode("utf-8"),
        file_name="filtered_measles_rubella_long.csv",
        mime="text/csv"
    )
