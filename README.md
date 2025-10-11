# Project-4-Digital-Banking

## Cara Menjalankan Proyek:

1.  **Persiapan Awal**

    Pastikan Anda memiliki Python 3.8+ terinstal.
    Clone repositori ini:
    ```bash
    git clone https://github.com/Jason160803/Project-4-Digital-Banking.git
    ```

2.  **Setup Virtual Environment**

    Sangat disarankan untuk menggunakan virtual environment agar dependensi proyek tidak tercampur.
    
    Menggunakan PowerShell:
    ```bash
    python -m venv venv
    ```

3.  **Aktivasi (Windows)**

    ```bash
    .\venv\Scripts\activate
    ```

4.  **Instal Dependensi**

    Instal semua library yang dibutuhkan dengan satu perintah:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Jalankan Server API**

    Jalankan server Uvicorn dari direktori utama proyek:
    ```bash
    uvicorn digital_banking.main:app --reload
    ```
    Server akan berjalan di http://127.0.0.1:8000.

---

## Fitur dan Konfigurasi

Semua pengaturan utama untuk aplikasi ini dapat ditemukan dalam file `digital_banking/config.py`.

| Konfigurasi                 | Nilai             | Deskripsi                                                                 |
| --------------------------- | ----------------- | ------------------------------------------------------------------------- |
| `MINIMUM_BALANCE`           | `20000.0`         | Saldo minimum yang harus tersisa di akun setelah penarikan atau transfer. |
| `INTER_BANK_TRANSFER_FEE`   | `5000.0`          | Biaya yang dikenakan untuk setiap transfer antar bank.                      |
| `MAX_TRANSFER_AMOUNT`       | `25000000.0`      | Jumlah maksimum yang dapat ditransfer dalam satu transaksi.               |
| `DAILY_TRANSACTION_LIMIT`   | `10`              | Batas jumlah transaksi harian per akun.                                   |
| `LOCAL_BANK_NAME`           | "Bank Digital API"| Nama bank lokal yang digunakan untuk menentukan biaya transfer.            |

---

## Cara Melakukan Pengujian:

1.  **Melalui Unit Test**

    Jalankan semua tes otomatis untuk memastikan fungsionalitas API berjalan dengan benar. `pytest` Semua tes harus PASS jika konfigurasi sudah benar.

2.  **Melalui file index.html**

    File ini berfungsi sebagai antarmuka pengujian sederhana dan lengkap. Pastikan server API sedang berjalan.



2. Melalui Antarmuka Web (UI)

Proyek ini dilengkapi dengan `index.html` yang berfungsi sebagai UI. Cara menjalankannya adalah sebagai berikut:

1.  **Pastikan Server API (Backend) Anda tetap berjalan** di satu terminal pada port `8000`.
2.  **Buka Terminal Baru**, masuk ke direktori proyek, dan aktifkan *virtual environment*.
3.  Di terminal kedua ini, jalankan perintah berikut untuk menyajikan file `index.html`:
    ```bash
    python -m http.server 8001
    ```
4.  Buka browser dan kunjungi `http://localhost:8001`. Anda akan melihat antarmuka web untuk menguji API.

3.  **Melalui Swagger UI**

    Anda juga dapat mengakses dokumentasi API interaktif yang dibuat otomatis oleh FastAPI. Buka browser dan kunjungi: http://127.0.0.1:8000/docs