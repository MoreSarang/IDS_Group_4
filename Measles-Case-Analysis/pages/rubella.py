import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_util import load_data


csv_data = load_data()
print(csv_data.head())


st.set_page_config(page_title="Rubella Case Analysis Dashboard", layout="wide")

st.title("ℹ️ Rubella Information Page")
st.write("This app provides information about Rubella.")


# ==========================================
# 1 Simple Rubella Cases Over Time
# ==========================================
def plot_rubella_cases_over_time(csv_data):
    # Set up nice styling
    plt.style.use('default')
    sns.set_palette("Set2")


    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Rubella Cases Analysis', fontsize=16, fontweight='bold')

    ax1 = axes[0, 0]

    # Get total rubella cases by year
    yearly_rubella = csv_data.groupby('year')['rubella_total'].sum()

    # Create a simple line plot with markers
    ax1.plot(yearly_rubella.index, yearly_rubella.values,
         marker='o', linewidth=3, markersize=8, color='#FF6B9D')
    ax1.fill_between(yearly_rubella.index, yearly_rubella.values, alpha=0.3, color='#FF6B9D')

    ax1.set_title('Total Rubella Cases Per Year', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of Cases')
    ax1.grid(True, alpha=0.3)

    # Add value labels on points
    for x, y in zip(yearly_rubella.index, yearly_rubella.values):
        if y > 0:  # Only label non-zero values
            ax1.annotate(f'{int(y):,}', (x, y), textcoords="offset points",
                    xytext=(0,10), ha='center', fontsize=9)
    
    # ==========================================
    # 2 Rubella Cases by WHO Region (Pie Chart)
    # ==========================================

    ax2 = axes[0, 1]

    # Get total cases by region
    region_rubella = csv_data.groupby('region')['rubella_total'].sum()
    region_rubella = region_rubella[region_rubella > 0]  # Only include regions with cases

    # Create a colorful pie chart
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF']
    wedges, texts, autotexts = ax2.pie(region_rubella.values, labels=region_rubella.index,
                                   autopct='%1.1f%%', startangle=90, colors=colors)

    ax2.set_title('Rubella Cases by WHO Region\n(Total Distribution)', fontsize=14, fontweight='bold')

    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    # ==========================================
    # 3 Top 10 Countries with Most Rubella Cases
    # ==========================================
    ax3 = axes[1, 0]

    # Get top 10 countries by rubella cases
    country_rubella = csv_data.groupby('country')['rubella_total'].sum().sort_values(ascending=False)
    top_10 = country_rubella.head(10)

    # Create horizontal bar chart
    bars = ax3.barh(range(len(top_10)), top_10.values, color='#4ECDC4')

    # Customize the chart
    ax3.set_yticks(range(len(top_10)))
    ax3.set_yticklabels(top_10.index)
    ax3.set_title('Top 10 Countries - Rubella Cases', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Total Cases')

    # Add value labels on bars
    for i, (country, value) in enumerate(top_10.items()):
        ax3.text(value + max(top_10) * 0.02, i, f'{int(value):,}',
             va='center', fontweight='bold')

    ax3.grid(axis='x', alpha=0.3)
    ax3.invert_yaxis()

    # ==========================================
    # 4 Rubella Lab Confirmation vs Total Cases
    # ==========================================
    ax4 = axes[1, 1]

    # Filter data for countries with rubella cases
    rubella_data = csv_data[(csv_data['rubella_total'] > 0) & (csv_data['rubella_lab_confirmed'] >= 0)]

    # Create scatter plot
    scatter = ax4.scatter(rubella_data['rubella_total'],
                     rubella_data['rubella_lab_confirmed'],
                     alpha=0.6, s=60, c='#95E1D3', edgecolors='black', linewidth=0.5)

    ax4.set_title('Lab Confirmed vs Total Rubella Cases', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Total Rubella Cases')
    ax4.set_ylabel('Lab Confirmed Cases')
    ax4.grid(True, alpha=0.3)

    # Add diagonal reference line (perfect confirmation)
    max_val = max(ax4.get_xlim()[1], ax4.get_ylim()[1])
    ax4.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, linewidth=2,
         label='Perfect Confirmation Line')
    ax4.legend()

    # Adjust layout
    plt.tight_layout()
    return plt


# ==========================================
# BONUS: Simple Summary Chart
# ==========================================
def simple_summary_chart(csv_data):
    plt.figure(figsize=(12, 6))

    # Create side-by-side comparison of measles vs rubella
    diseases = ['Measles', 'Rubella']
    total_cases = [csv_data['measles_total'].sum(), csv_data['rubella_total'].sum()]
    confirmed_cases = [csv_data['measles_lab_confirmed'].sum(), csv_data['rubella_lab_confirmed'].sum()]

    x = np.arange(len(diseases))
    width = 0.35

    bars1 = plt.bar(x - width/2, total_cases, width, label='Total Cases',
                color=['#FF6B6B', '#4ECDC4'], alpha=0.8)
    bars2 = plt.bar(x + width/2, confirmed_cases, width, label='Lab Confirmed',
                color=['#FF8E8E', '#7FDDDD'], alpha=0.8)

    plt.title('Measles vs Rubella: Total and Lab Confirmed Cases', fontsize=16, fontweight='bold')
    plt.ylabel('Number of Cases')
    plt.xticks(x, diseases)
    plt.legend()

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + max(total_cases) * 0.01,
                f'{int(height):,}', ha='center', va='bottom', fontweight='bold')

    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return plt

def main():
    csv_data = load_data()

    plt = plot_rubella_cases_over_time(csv_data)
    st.pyplot(plt)
    plt1 = simple_summary_chart(csv_data)
    st.pyplot(plt1)

    
if __name__ == "__main__":
    main()
