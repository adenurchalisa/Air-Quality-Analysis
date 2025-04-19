# Analisis Kualitas Udara Beijing

Dashboard interaktif untuk menganalisis data kualitas udara di Beijing dari 2013-2017.

## Fitur
- Visualisasi tren polutan utama
- Perbandingan antar stasiun pemantauan
- Analisis pola musiman dan harian

## Cara Menggunakan
1. Pilih rentang waktu
2. Pilih stasiun pemantauan
3. Jelajahi visualisasi

## Data Source
Data berasal dari 12 stasiun pemantauan kualitas udara di Beijing.

## URL Aplikasi
[Dashboard Interaktif](https://air-quality-analysis-5pragjde3af23gzj5vonv8.streamlit.app/)

---

## Setup Proyek

### 1. Membuat Virtual Environment
Untuk memastikan lingkungan pengembangan tetap bersih, buatlah virtual environment:

```bash
python -m venv env
```

Aktifkan virtual environment:
- **Windows**: `.\env\Scripts\activate`
- **macOS/Linux**: `source env/bin/activate`

### 2. Menginstal Dependensi
Pastikan semua library yang dibutuhkan diinstal melalui `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Menjalankan Dashboard
Setelah dependensi terinstal, jalankan file Streamlit dashboard:

```bash
streamlit run app.py
```

Pastikan file data berada di path yang sesuai seperti yang didefinisikan dalam kode.

---

## Catatan
- Gunakan data yang sudah dibersihkan (cleaned data) untuk memastikan hasil visualisasi sesuai dengan analisis data di notebook.
- Pilihan stasiun di sidebar akan secara default memuat semua stasiun untuk konsistensi dengan notebook.