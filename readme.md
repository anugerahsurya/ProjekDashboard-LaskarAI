# Dashboard Kualitas Udara berdasarkan PM2.5 ✨

**Halo!**  
Untuk menjalankan *Dashboard* di perangkat kamu, ikuti langkah-langkah berikut untuk menyiapkan environment dan menjalankan aplikasi.

---

## 1. Setup Environment
### Menggunakan Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### Menggunakan Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

---

## 2. Struktur Folder
```
proyek_analisis_data/
├── Dashboard/
│   ├── main_data.csv
│   ├── ProjekDashboard.py
│   ├── requirements.txt
├── DataGabungan.csv
├── Proyek_Analisis_Data.ipynb
├── readme.md
├── requirements.txt
├── url.txt
├── PRSA_Data_20130301-20170228/
```

---

## 3. Menjalankan Dashboard
Gunakan perintah berikut untuk menjalankan aplikasi dengan *Streamlit*:
```
cd Dashboard
streamlit run ProjekDashboard.py
```

Selamat mencoba! 🚀

