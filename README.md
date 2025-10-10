# Project-4-Digital-Banking

# Cara Menjalankan Proyek:

1. Persiapan Awal
Pastikan Anda memiliki Python 3.8+ terinstal.# 
Clone repositori ini:
git clone [https://github.com/Jason160803/Project-4-Digital-Banking.git](https://github.com/Jason160803/Project-4-Digital-Banking.git)

2. Setup Virtual EnvironmentSangat disarankan untuk menggunakan virtual environment agar dependensi proyek tidak tercampur
Menggunakan PowerShell
python -m venv venv

# Aktivasi (Windows)
3. .\venv\Scripts\activate

4. Instal Dependensi
Instal semua library yang dibutuhkan dengan satu perintah:
pip install -r requirements.txt

5. Jalankan Server APIJalankan server Uvicorn dari direktori utama proyek:
uvicorn digital_banking.main:app --reload

Server akan berjalan di http://127.0.0.1:8000.Cara Melakukan Pengujian

A. Melalui Unit Test:
Jalankan semua tes otomatis untuk memastikan fungsionalitas API berjalan dengan benar. pytest Semua tes harus PASS jika konfigurasi sudah benar.

B. Melalui Antarmuka Web (UI)Proyek ini dilengkapi dengan index.
html yang berfungsi sebagai antarmuka pengujian sederhana dan lengkap.Pastikan server API sedang berjalan.
Buka file index.html.
Gunakan formulir yang tersedia untuk berinteraksi dengan semua fitur API secara visual.

C. Melalui Swagger UIAnda juga dapat mengakses dokumentasi API interaktif yang dibuat otomatis oleh FastAPI.Buka browser dan kunjungi: http://127.0.0.1:8000/docs