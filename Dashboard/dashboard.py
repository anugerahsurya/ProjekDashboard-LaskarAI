import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

def kategori_pm25(value):
    if value <= 15:
        return "Baik"
    elif value <= 65:
        return "Sedang"
    elif value <= 150:
        return "Tidak Sehat"
    elif value <= 250:
        return "Sangat Tidak Sehat"
    else:
        return "Berbahaya"

kategori_colors = {
    "Baik": "#2E8B57",
    "Sedang": "#FFD700",
    "Tidak Sehat": "#FF8C00",
    "Sangat Tidak Sehat": "#DC143C",
    "Berbahaya": "#8B0000"
}

def plot_time_series(df, station, datetime_col, value_col):
    station_data = df[df['station'] == station].copy()
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 10))
    ax_ts, ax_bar = axes
    
    ax_ts.plot(station_data[datetime_col], station_data[value_col], label=f"{station}", color='b')
    
    x_vals = (station_data[datetime_col] - station_data[datetime_col].min()).dt.days.values
    y_vals = station_data[value_col].values
    slope, intercept, _, _, _ = linregress(x_vals, y_vals)
    ax_ts.plot(station_data[datetime_col], slope * x_vals + intercept, color='r', linestyle='--', label=f'Linear Fit (slope={slope:.2f})')
    
    ax_ts.set_title(f"Time Series for {station}")
    ax_ts.set_xlabel("Date")
    ax_ts.set_ylabel(value_col)
    ax_ts.legend()
    ax_ts.grid(True)
    
    station_data["month"] = station_data[datetime_col].dt.month
    monthly_avg = station_data.groupby("month")[value_col].mean()
    
    ax_bar.bar(monthly_avg.index, monthly_avg.values, color='g', alpha=0.7)
    ax_bar.set_title(f"Monthly Average for {station}")
    ax_bar.set_xlabel("Month")
    ax_bar.set_ylabel(f"Avg {value_col}")
    ax_bar.set_xticks(np.arange(1, 13))
    ax_bar.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax_bar.grid(True)
    
    st.pyplot(fig)

# Load dataset
df_daily = pd.read_csv("main_data.csv")  # Gantilah dengan lokasi data yang sesuai
df_daily["datetime"] = pd.to_datetime(df_daily["datetime"])

st.title("Air Quality Dashboard")

station_list = df_daily["station"].unique()
selected_station = st.selectbox("Select a station:", station_list)

end_date = df_daily['datetime'].max()
start_date = end_date - pd.DateOffset(years=1)
filtered_data = df_daily[(df_daily['station'] == selected_station) & (df_daily['datetime'] >= start_date)]

filtered_data['year'] = filtered_data['datetime'].dt.year
filtered_data['month'] = filtered_data['datetime'].dt.month
filtered_data['week'] = filtered_data['datetime'].dt.isocalendar().week
filtered_data['day'] = filtered_data['datetime'].dt.dayofweek
filtered_data['category'] = filtered_data['PM2.5'].apply(kategori_pm25)

hari_labels = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
unique_months = filtered_data[['year', 'month']].drop_duplicates().sort_values(by=['year', 'month'])
n_months = len(unique_months)

col1, col2 = st.columns(2)

with col1:
    st.subheader("PM2.5 Heatmap")
    fig, axes = plt.subplots((n_months // 3) + (n_months % 3 > 0), 3, figsize=(18, (n_months // 3) * 5))
    axes = axes.flatten()
    fig.suptitle("PM2.5 Wilayah 1 Tahun Terakhir", fontsize=16, fontweight='bold')
    
    for i, (year, month) in enumerate(unique_months.itertuples(index=False)):
        monthly_data = filtered_data[(filtered_data['year'] == year) & (filtered_data['month'] == month)]
        if monthly_data.empty:
            continue
        
        heatmap_data = monthly_data.pivot_table(index='week', columns='day', values='PM2.5')
        sns.heatmap(heatmap_data, cmap=sns.color_palette(list(kategori_colors.values())), annot=False, linewidths=0.5, ax=axes[i], cbar=False)
        axes[i].set_title(f'Periode - {year}-{month:02d}')
        axes[i].set_xlabel("Hari")
        axes[i].set_ylabel("Minggu")
        axes[i].set_xticks(np.arange(len(hari_labels)) + 0.5)
        axes[i].set_xticklabels(hari_labels, rotation=45)
        axes[i].tick_params(left=False, labelleft=False)
    
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig)

with col2:
    st.subheader("Time Series Analysis")
    plot_time_series(df_daily, selected_station, "datetime", "PM2.5")

with st.container():
    st.subheader("Catatan")
    notes = "Ini adalah catatan statis yang ditentukan oleh pengembang."
    st.markdown(notes)
