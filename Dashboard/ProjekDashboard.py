import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import linregress
import plotly.express as px
import plotly.graph_objects as go

# Fungsi kategori PM2.5
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

kategori_warna = {
    "Baik": "#2E8B57",
    "Sedang": "#FADA7A",
    "Tidak Sehat": "#FF8C00",
    "Sangat Tidak Sehat": "#DC143C",
    "Berbahaya": "#8B0000"
}

# Konfigurasi halaman
st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="https://laskarai.id/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit as st

# Menambahkan kode CSS untuk memberikan warna pada sidebar laman dashboard
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #859F3D;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load dataset
df_daily = pd.read_csv("Dashboard/main_data.csv")  # Sesuaikan lokasi file
df_daily["datetime"] = pd.to_datetime(df_daily["datetime"])
df_daily["year"] = df_daily["datetime"].dt.year 
df_daily["month"] = df_daily["datetime"].dt.month
df_daily["week"] = df_daily["datetime"].dt.isocalendar().week
df_daily["day"] = df_daily["datetime"].dt.dayofweek

# Sidebar
with st.sidebar:
    st.write("Anugerah Surya Atmaja (A-13)")
    st.title("Dashboard Kualitas Udara")
    st.write("ditinjau berdasarkan Particulate Matter 2.5")
    station_list = df_daily["station"].unique()
    selected_station = st.selectbox("Pilih Stasiun Observasi:", station_list)
    
    end_date = df_daily['datetime'].max()
    start_date = end_date - pd.DateOffset(years=1)
    
    selected_year = st.selectbox("Pilih Tahun Amatan :", sorted(df_daily["year"].unique(), reverse=True))
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober','November','Desember']
    selected_month = st.selectbox("Pilih Bulan Amatan :", list_bulan)
    selected_month_index = list_bulan.index(selected_month) + 1 

    filtered_data = df_daily[(df_daily['station'] == selected_station) & (df_daily["year"] == selected_year) & (df_daily["month"] == selected_month_index)].copy()
    filtered_data["category"] = filtered_data["PM2.5"].apply(kategori_pm25)

# Fungsi Plot Time Series
def buatVisualisasiTS(data, station, datetime_col, value_col):
    station_data = data.copy()

    fig, axes = plt.subplots(2, 1, figsize=(10, 10))
    ax_ts, ax_bar = axes

    ax_ts.plot(station_data[datetime_col], station_data[value_col], label=f"{station}", color='b')

    # Linear regression
    x_vals = (station_data[datetime_col] - station_data[datetime_col].min()).dt.days.values
    y_vals = station_data[value_col].values
    slope, intercept, _, _, _ = linregress(x_vals, y_vals)
    ax_ts.plot(station_data[datetime_col], slope * x_vals + intercept, color='r', linestyle='--', label=f'Linear Fit (slope={slope:.2f})')

    ax_ts.set_title(f"Time Series for {station}")
    ax_ts.set_xlabel("Date")
    ax_ts.set_ylabel(value_col)
    ax_ts.legend()
    ax_ts.grid(True)

    # Monthly Average
    station_data["month"] = station_data[datetime_col].dt.month
    monthly_avg = station_data.groupby("month")[value_col].mean()

    ax_bar.bar(monthly_avg.index, monthly_avg.values, color='g', alpha=0.7)
    ax_bar.set_title(f"Rata-rata bulanan PM2.5 di Stasiun {station}")
    ax_bar.set_xlabel("Bulan")
    ax_bar.set_ylabel(f"Rata-rata {value_col}")
    ax_bar.set_xticks(np.arange(1, 13))
    ax_bar.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax_bar.set_ylim(0, 150)
    ax_bar.grid(True)

    st.pyplot(fig)

# Fungsi Heatmap Interaktif
def buatHeatmap(dataset, station, year, month):
    dataset = dataset.copy()
    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    
    filtered_data = dataset[(dataset['station'] == station) & (dataset['year'] == year) & (dataset['month'] == month)]
    
    if filtered_data.empty:
        st.warning("Data tidak ditemukan untuk parameter yang diberikan.")
        return
    
    filtered_data["week"] = filtered_data["datetime"].dt.isocalendar().week
    filtered_data["day"] = filtered_data["datetime"].dt.dayofweek
    
    heatmap_data = filtered_data.pivot_table(index='week', columns='day', values='PM2.5')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
        y=heatmap_data.index,
        colorscale=[[0, kategori_warna["Baik"]], 
                    [0.25, kategori_warna["Sedang"]],
                    [0.5, kategori_warna["Tidak Sehat"]],
                    [0.75, kategori_warna["Sangat Tidak Sehat"]],
                    [1, kategori_warna["Berbahaya"]]],
        hoverongaps=False,
        text=heatmap_data.values.astype(int),
        hoverinfo="text",
    ))
    
    fig.update_layout(
        title=f"Heatmap PM2.5 - {station} ({year}-{month:02d})",
        xaxis_title="Hari",
        yaxis_title="Minggu",
        yaxis=dict(showticklabels=False),
    )
    
    st.plotly_chart(fig)


col1, col2 = st.columns((3, 2))

# Kolom 1 : Time Series
with col1:
    st.markdown("<h3 style='text-align: center;'>Visualisasi Data Runtun Waktu</h3>", unsafe_allow_html=True)
    buatVisualisasiTS(filtered_data, selected_station, "datetime", "PM2.5")

# Kolom 2 : Heatmap
with col2:
    st.subheader(f"Sebaran PM2.5 di Stasiun {selected_station}")
    buatHeatmap(filtered_data, selected_station, selected_year, selected_month_index)