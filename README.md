Cara Menjalankan Proyek:

1. Persiapan AwalPastikan Anda memiliki Python 3.8+ terinstal.# Clone repositori ini (jika belum)
git clone [https://github.com/Jason160803/Project-4-Digital-Banking.git](https://github.com/Jason160803/Project-4-Digital-Banking.git)

2. Setup Virtual EnvironmentSangat disarankan untuk menggunakan virtual environment agar dependensi proyek tidak tercampur
Menggunakan PowerShell
python -m venv venv

# Aktivasi (Windows)
.\venv\Scripts\activate

# Aktivasi (macOS/Linux)
# source venv/bin/activate

3. Instal DependensiInstal semua library yang dibutuhkan dengan satu perintah.pip install -r requirements.txt

4. Jalankan Server APIJalankan server Uvicorn dari direktori utama proyek.uvicorn digital_banking.main:app --reload
Server akan berjalan di http://127.0.0.1:8000.Cara Melakukan Pengujian
A. Melalui Unit TestJalankan semua tes otomatis untuk memastikan fungsionalitas API berjalan dengan benar.pytest
Semua tes harus PASS jika konfigurasi sudah benar.
B. Melalui Antarmuka Web (UI)Proyek ini dilengkapi dengan index.html yang berfungsi sebagai antarmuka pengujian sederhana dan lengkap.Pastikan server API sedang berjalan.Buka file index.html langsung di browser Anda (cukup klik dua kali filenya).Gunakan formulir yang tersedia untuk berinteraksi dengan semua fitur API secara visual.
C. Melalui Swagger UIAnda juga dapat mengakses dokumentasi API interaktif yang dibuat otomatis oleh FastAPI.Buka browser dan kunjungi: http://127.0.0.1:8000/docs



Project 4: Digital Banking API
Ini adalah proyek simulasi layanan perbankan sederhana berbasis API yang dikembangkan sebagai bagian dari Ujian Tengah Semester untuk mata kuliah Kapita Selekta Analitika Data. 
API ini dibangun menggunakan FastAPI dan dirancang untuk berjalan tanpa database persisten, sesuai dengan batasan proyek.Repositori ini mencakup backend API, unit test yang komprehensif, dan antarmuka web sederhana untuk pengujian.
Fitur UtamaAPI ini memiliki dua peran utama: Admin dan Nasabah.Fitur AdminMembuat Akun Baru: Admin dapat membuat akun baru untuk nasabah dengan menyertakan nama, nama bank, 6-digit PIN, dan saldo awal yang harus memenuhi saldo minimum yang ditetapkan.Melihat Daftar Akun: Admin dapat melihat daftar semua akun yang terdaftar beserta informasi dasarnya (nama, no. rekening, nama bank, status aktif), namun tidak dapat melihat informasi sensitif seperti saldo atau riwayat transaksi.Memperbarui Nama Nasabah: Admin dapat mengubah nama nasabah berdasarkan nomor rekening.Menghapus Akun: Admin dapat menghapus akun nasabah secara permanen. Semua data terkait akun tersebut, termasuk riwayat transaksi, akan dihilangkan dari sistem.Fitur NasabahOtorisasi Berbasis PIN: Setiap transaksi keuangan (deposit, tarik, transfer) memerlukan PIN 6-digit yang benar untuk otorisasi.Cek Detail Akun: Nasabah dapat melihat detail akun mereka, termasuk saldo saat ini dan jumlah transaksi transfer yang telah dilakukan hari itu.Setor Tunai (Deposit): Menambahkan saldo ke rekening. Transaksi ini tidak dihitung dalam limit transaksi harian.Tarik Tunai (Withdraw): Mengurangi saldo dari rekening, dengan validasi untuk memastikan saldo tidak jatuh di bawah batas minimum. Transaksi ini tidak dihitung dalam limit transaksi harian.Transfer: Mentransfer dana ke rekening lain. Akan dikenakan biaya admin jika transfer dilakukan ke bank yang berbeda. Fitur ini divalidasi oleh batas transaksi harian dan batas nominal per transaksi.Lihat Riwayat Transaksi: Nasabah dapat melihat seluruh riwayat transaksi yang pernah dilakukan, lengkap dengan format waktu WIB (DD-MM-YYYY, HH:MM:SS).Aturan Bisnis & KonfigurasiSemua aturan bisnis utama dapat diatur secara terpusat melalui file digital_banking/config.py:Saldo Minimum: Rp 20.000Biaya Transfer Antarbank: Rp 5.000Limit Maksimum per Transfer: Rp 25.000.000Limit Transaksi Harian (untuk transfer): 10 kaliTeknologi yang DigunakanBackend: Python 3, FastAPIValidasi Data: PydanticTesting: PytestServer: UvicornPenyimpanan Data: In-memory (Python Dictionary)Struktur ProyekProject-4-Digital-Banking/
├── digital_banking/
│   ├── routers/
│   │   ├── admin.py        # Endpoint untuk admin
│   │   └── customer.py     # Endpoint untuk nasabah
│   ├── config.py           # Konfigurasi pusat untuk aturan bisnis
│   ├── database.py         # Penyimpanan data in-memory
│   ├── main.py             # Titik masuk utama aplikasi FastAPI
│   ├── models.py           # Skema data Pydantic
│   └── services.py         # Logika bisnis inti
├── tests/
│   ├── test_admin_api.py   # Unit test untuk fitur admin
│   └── test_customer_api.py  # Unit test untuk fitur nasabah
├── index.html              # Antarmuka web sederhana untuk pengujian
└── requirements.txt        # Daftar dependensi Python

