import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from PIL import Image

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Kualitas Udara Beijing",
    page_icon="",
    layout="wide",
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    import os
    import glob
    
    # Path ke folder dataset yang berisi file-file CSV
    dataset_folder = '../notebook/PRSA_Data_20130301-20170228'
    
    # Cari semua file di dalam folder (tidak hanya CSV)
    all_files_in_folder = os.listdir(dataset_folder)
    
    # Cari semua file CSV di dalam folder
    all_csv_files = glob.glob(os.path.join(dataset_folder, "*.csv"))
    
    # Jika tidak ada file CSV, periksa file dengan ekstensi lain
    if not all_csv_files:
        for file in all_files_in_folder:
            full_path = os.path.join(dataset_folder, file)
            if os.path.isfile(full_path):
                st.write(f"Ekstensi file: {os.path.splitext(file)[1]}")
    
    # Buat list untuk menyimpan dataframe dari masing-masing file
    df_list = []
    
    # Baca setiap file CSV dan gabungkan
    for file in all_csv_files:
        try:
            df_temp = pd.read_csv(file)
            df_list.append(df_temp)
        except Exception as e:
            st.error(f"Error membaca file {file}: {str(e)}")
    
    # Gabungkan semua dataframe
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        
        # Konversi kolom tanggal dan waktu
        df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        
        # Penanganan data missing
        df_clean = df.dropna(subset=['PM2.5', 'PM10', 'SO2', 'NO2'])
        return df_clean
    else:
        st.error("Tidak ada file CSV yang ditemukan di folder dataset!")
        return pd.DataFrame()  # Return empty dataframe if no files found

# Load data
df_clean = load_data()

# Header Dashboard
st.title("Dashboard Analisis Kualitas Udara Beijing 2013-2017")
st.markdown("""
Dashboard ini menampilkan hasil analisis kualitas udara Beijing dari tahun 2013 hingga 2017 berdasarkan data dari stasiun pemantauan.
Analisis berfokus pada dua pertanyaan utama:
1. Bagaimana tren polutan utama berubah sepanjang waktu?
2. Bagaimana perbandingan kualitas udara berdasarkan lokasi?
""")

# Sidebar
st.sidebar.header("Filter Data")

# Filter berdasarkan tahun
years = df_clean['year'].unique()
selected_years = st.sidebar.multiselect(
    "Pilih Tahun", 
    options=years, 
    default=years
)

# Filter berdasarkan stasiun
stations = df_clean['station'].unique()
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun Pemantauan", 
    options=stations, 
    default=stations[:3]  # Default: 3 stasiun pertama
)

# Filter data berdasarkan input user
filtered_df = df_clean[
    (df_clean['year'].isin(selected_years)) & 
    (df_clean['station'].isin(selected_stations))
]

# Menampilkan overview dataset
st.header("Ringkasan Dataset")
st.write(f"Jumlah data: {filtered_df.shape[0]:,} baris")
st.write(f"Rentang waktu: {filtered_df['date'].min().strftime('%d %B %Y')} hingga {filtered_df['date'].max().strftime('%d %B %Y')}")

# Tampilkan kolom-kolom utama jika dicentang
if st.checkbox("Tampilkan 10 data teratas"):
    st.dataframe(filtered_df[['date', 'station', 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].head(10))

# Tab untuk memisahkan analisis berdasarkan pertanyaan penelitian
tab1, tab2 = st.tabs(["Tren Temporal Polutan", "Perbandingan Kualitas Udara Lokasi"])

# Tab 1: Tren Temporal Polutan
with tab1:
    st.header("Tren Polutan Berdasarkan Waktu")
    
    # Analisis tahunan
    st.subheader("Tren Tahunan Polutan Utama")
    # Agregasi data per tahun
    yearly_avg = filtered_df.groupby('year')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Pilihan polutan untuk visualisasi
    polutan_options = st.multiselect(
        "Pilih Polutan untuk Visualisasi Tahunan", 
        options=['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'], 
        default=['PM2.5', 'PM10']
    )
    
    for polutan in polutan_options:
        ax.plot(yearly_avg['year'], yearly_avg[polutan], 'o-', linewidth=2, label=polutan)
    
    ax.set_title("Tren Tahunan Polutan Udara", fontsize=15)
    ax.set_xlabel("Tahun", fontsize=12)
    ax.set_ylabel("Konsentrasi (μg/m³)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

    # Tampilkan insight penting
    if 'PM2.5' in polutan_options:
        first_year = yearly_avg['year'].iloc[0]
        last_year = yearly_avg['year'].iloc[-1]
        pm25_change = ((yearly_avg.loc[yearly_avg['year'] == last_year, 'PM2.5'].values[0] -
                        yearly_avg.loc[yearly_avg['year'] == first_year, 'PM2.5'].values[0]) / 
                      yearly_avg.loc[yearly_avg['year'] == first_year, 'PM2.5'].values[0] * 100)
        
        st.info(f"💡 **Insight:** Konsentrasi PM2.5 menunjukkan perubahan sekitar {pm25_change:.1f}% dari {first_year} hingga {last_year}.")
    
    # Analisis musiman
    st.subheader("Pola Musiman Polutan")
    # Hitung rata-rata bulanan
    filtered_df['month'] = filtered_df['date'].dt.month
    monthly_avg = filtered_df.groupby('month')[['PM2.5', 'PM10', 'SO2', 'NO2']].mean().reset_index()
    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun',
                   7:'Jul', 8:'Agt', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
    
    # Pilihan polutan untuk visualisasi musiman
    seasonal_polutan = st.selectbox(
        "Pilih Polutan untuk Visualisasi Musiman", 
        options=['PM2.5', 'PM10', 'SO2', 'NO2'], 
        index=0
    )
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(monthly_avg['month'], monthly_avg[seasonal_polutan], 'o-', linewidth=2, color='#1f77b4')
    ax.set_title(f"Pola Musiman {seasonal_polutan}", fontsize=15)
    ax.set_xlabel("Bulan", fontsize=12)
    ax.set_ylabel(f"Konsentrasi {seasonal_polutan} (μg/m³)", fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([month_names[m] for m in range(1, 13)])
    ax.grid(True, alpha=0.3)
    
    # Highlight bulan dengan nilai tertinggi dan terendah
    max_month = monthly_avg.loc[monthly_avg[seasonal_polutan].idxmax(), 'month']
    min_month = monthly_avg.loc[monthly_avg[seasonal_polutan].idxmin(), 'month']
    max_val = monthly_avg[seasonal_polutan].max()
    min_val = monthly_avg[seasonal_polutan].min()
    
    ax.plot(max_month, max_val, 'ro', markersize=10)
    ax.annotate(f'Tertinggi: {max_val:.1f}', xy=(max_month, max_val), 
                xytext=(max_month, max_val*1.1), ha='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))
    
    ax.plot(min_month, min_val, 'go', markersize=10)
    ax.annotate(f'Terendah: {min_val:.1f}', xy=(min_month, min_val), 
                xytext=(min_month, min_val*0.9), ha='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="lightgreen", alpha=0.7))
    
    st.pyplot(fig)
    
    st.info(f"💡 **Insight:** {seasonal_polutan} tertinggi pada bulan {month_names[max_month]} ({max_val:.1f} μg/m³) dan terendah pada bulan {month_names[min_month]} ({min_val:.1f} μg/m³).")
    
    # Analisis harian
    st.subheader("Pola Harian Polutan")
    # Hitung rata-rata per jam
    hourly_avg = filtered_df.groupby('hour')[['PM2.5', 'PM10']].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(hourly_avg['hour'], hourly_avg['PM2.5'], 'o-', linewidth=2, label='PM2.5')
    ax.plot(hourly_avg['hour'], hourly_avg['PM10'], 's-', linewidth=2, label='PM10')
    ax.set_title("Pola Harian Polutan", fontsize=15)
    ax.set_xlabel("Jam", fontsize=12)
    ax.set_ylabel("Konsentrasi (μg/m³)", fontsize=12)
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, alpha=0.3)
    
    # Highlight jam sibuk
    ax.axvspan(7, 9, alpha=0.2, color='orange', label='Jam Sibuk Pagi')
    ax.axvspan(17, 19, alpha=0.2, color='purple', label='Jam Sibuk Sore')
    ax.legend()
    
    st.pyplot(fig)
    
    max_pm25_hour = hourly_avg.loc[hourly_avg['PM2.5'].idxmax(), 'hour']
    min_pm25_hour = hourly_avg.loc[hourly_avg['PM2.5'].idxmin(), 'hour']
    
    st.info(f"💡 **Insight:** PM2.5 tertinggi pada jam {max_pm25_hour}:00 dan terendah pada jam {min_pm25_hour}:00. Puncak polusi terjadi pada jam-jam sibuk pagi dan sore hari.")

# Tab 2: Perbandingan Kualitas Udara Lokasi
with tab2:
    st.header("Perbandingan Kualitas Udara Berdasarkan Lokasi")
    
    # Rata-rata PM2.5 per stasiun
    st.subheader("Perbandingan PM2.5 antar Stasiun")
    
    station_avg = filtered_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False).reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(station_avg['station'], station_avg['PM2.5'], color='skyblue')
    
    # Tambahkan nilai pada bar chart
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}', ha='center', va='bottom')
    
    ax.set_title("Rata-rata PM2.5 per Stasiun", fontsize=15)
    ax.set_xlabel("Stasiun", fontsize=12)
    ax.set_ylabel("Rata-rata PM2.5 (μg/m³)", fontsize=12)
    ax.axhline(y=15, color='red', linestyle='--', label='WHO Guideline (15 μg/m³)')
    ax.set_xticklabels(station_avg['station'], rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)
    
    highest_station = station_avg['station'].iloc[0]
    lowest_station = station_avg['station'].iloc[-1]
    highest_val = station_avg['PM2.5'].iloc[0]
    lowest_val = station_avg['PM2.5'].iloc[-1]
    
    st.info(f"""
    💡 **Insight:** 
    - Stasiun dengan PM2.5 tertinggi: {highest_station} ({highest_val:.1f} μg/m³)
    - Stasiun dengan PM2.5 terendah: {lowest_station} ({lowest_val:.1f} μg/m³)
    - Perbedaan: {highest_val - lowest_val:.1f} μg/m³ ({highest_val/lowest_val:.2f}x lipat)
    """)
    
    # Box plots untuk distribusi PM2.5
    st.subheader("Distribusi PM2.5 per Stasiun")
    
    # Pilihan stasiun untuk box plot
    # Pertama, dapatkan daftar stasiun yang valid dalam data yang difilter
    valid_stations = filtered_df['station'].unique()

    # Tampilkan pesan jika stasiun yang dipilih di filter utama tidak memiliki data
    if len(valid_stations) < len(selected_stations):
        missing_stations = set(selected_stations) - set(valid_stations)
        st.warning(f"⚠️ Stasiun berikut tidak memiliki data yang cukup setelah filtering: {', '.join(missing_stations)}")

    # Gunakan stasiun yang valid sebagai opsi default
    box_stations = st.multiselect(
        "Pilih Stasiun untuk Visualisasi Box Plot", 
        options=valid_stations,
        default=valid_stations.tolist() if len(valid_stations) <= 5 else valid_stations[:5].tolist()
    )

    if box_stations:
        box_data = filtered_df[filtered_df['station'].isin(box_stations)]
        
        # Pastikan ada data untuk divisualisasikan
        if not box_data.empty:
            fig, ax = plt.subplots(figsize=(14, 7))
            sns.boxplot(x='station', y='PM2.5', data=box_data, ax=ax)
            ax.axhline(y=15, color='red', linestyle='--', label='WHO Guideline')
            ax.set_title("Distribusi PM2.5 per Stasiun", fontsize=15)
            ax.set_xlabel("Stasiun", fontsize=12)
            ax.set_ylabel("PM2.5 (μg/m³)", fontsize=12)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            st.pyplot(fig)
            
            # Tambahkan statistik ringkasan
            st.write("### Statistik Deskriptif PM2.5 per Stasiun")
            stats_df = box_data.groupby('station')['PM2.5'].describe().round(1)
            st.dataframe(stats_df[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']])
            
            st.info("💡 **Insight:** Box plot menunjukkan variasi dan outlier PM2.5 di masing-masing stasiun. Box yang lebih tinggi menandakan kualitas udara yang lebih buruk, dan box yang lebih lebar menunjukkan variabilitas yang lebih tinggi.")
        else:
            st.warning("Tidak ada data yang cukup untuk stasiun yang dipilih. Coba pilih stasiun lain atau ubah filter.")
    else:
        st.info("Silakan pilih stasiun untuk menampilkan box plot.")
    # Heatmap polutan per stasiun
    st.subheader("Rata-rata Berbagai Polutan per Stasiun")
    
    station_pollutants = filtered_df.groupby('station')[['PM2.5', 'PM10', 'SO2', 'NO2']].mean()
    station_pollutants = station_pollutants.reindex(station_avg['station'])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(station_pollutants, annot=True, cmap='YlOrRd', fmt='.1f', linewidths=.5, ax=ax)
    ax.set_title("Heatmap Rata-rata Polutan per Stasiun", fontsize=15)
    
    st.pyplot(fig)
    
    st.info("💡 **Insight:** Heatmap menunjukkan hubungan antar berbagai polutan di setiap stasiun. Warna yang lebih gelap menunjukkan konsentrasi yang lebih tinggi.")

# Kesimpulan
st.header("Kesimpulan")
st.markdown("""
#### Tren Polutan Sepanjang Waktu
Kualitas udara di Beijing membaik dari tahun 2013 hingga 2017, namun masih menunjukkan pola yang jelas terkait waktu. Polusi terburuk terjadi saat musim dingin dan di jam-jam sibuk (pagi dan sore). Udara paling bersih terjadi di bulan musim panas dan saat dini hari ketika aktivitas manusia minimal.

#### Perbandingan Kualitas Udara Antar Lokasi
Tidak semua area di Beijing sama buruknya - beberapa lokasi memiliki udara yang jauh lebih tercemar dibanding lokasi lain. Meskipun ada variasi, hampir semua stasiun pemantauan menunjukkan kadar PM2.5 di atas standar WHO (15 μg/m³), yang menunjukkan bahwa polusi udara masih menjadi tantangan kesehatan masyarakat di seluruh kota.

#### Kesimpulan Umum
Meskipun ada perbaikan selama periode pengamatan, Beijing masih perlu terus berupaya mengurangi polusi udara, dengan perhatian khusus pada area yang paling tercemar dan saat-saat ketika polusi cenderung memburuk (musim dingin dan jam sibuk).
""")

# Footer
st.markdown("---")
st.markdown("Dashboard dibuat oleh Ade Nurchalisa")