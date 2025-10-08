// Menunggu sampai seluruh halaman HTML dimuat
document.addEventListener('DOMContentLoaded', () => {
    
    // Mengambil elemen formulir dari HTML
    const form = document.getElementById('create-account-form');
    const responseMessageDiv = document.getElementById('response-message');

    // Menambahkan 'event listener' yang akan berjalan saat formulir di-submit
    form.addEventListener('submit', async (event) => {
        // Mencegah formulir mengirim data dengan cara default (reload halaman)
        event.preventDefault();

        // Mengambil data dari input fields
        const name = document.getElementById('name').value;
        const bank_name = document.getElementById('bank_name').value;
        const initial_deposit = parseFloat(document.getElementById('initial_deposit').value);

        // Menyiapkan data untuk dikirim dalam format JSON
        const formData = {
            name: name,
            bank_name: bank_name,
            initial_deposit: initial_deposit
        };

        // Mengirim data ke API FastAPI menggunakan 'fetch'
        try {
            const response = await fetch('http://127.0.0.1:8000/admin/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            // Mengambil data JSON dari respons API
            const result = await response.json();
            
            responseMessageDiv.style.display = 'block'; // Tampilkan elemen pesan

            if (response.ok) { // Jika status code 2xx (e.g., 201 Created)
                // Menampilkan pesan sukses
                responseMessageDiv.className = 'success';
                responseMessageDiv.innerHTML = `<strong>Berhasil!</strong> Akun untuk ${result.name} dibuat.<br>
                                                 Nomor Rekening: <strong>${result.account_number}</strong>`;
                form.reset(); // Mengosongkan formulir
            } else {
                // Menampilkan pesan error dari API
                responseMessageDiv.className = 'error';
                responseMessageDiv.innerHTML = `<strong>Gagal!</strong> ${result.detail}`;
            }

        } catch (error) {
            // Menangani error jika API tidak bisa dihubungi
            responseMessageDiv.style.display = 'block';
            responseMessageDiv.className = 'error';
            responseMessageDiv.innerHTML = '<strong>Error!</strong> Tidak dapat terhubung ke server.';
            console.error('Fetch error:', error);
        }
    });
});

// LETAKKAN KODE INI DI BAGIAN BAWAH FILE app.js

// === LOGIKA UNTUK FORM DEPOSIT ===
const depositForm = document.getElementById('deposit-form');
const depositResponseMessageDiv = document.getElementById('deposit-response-message');

depositForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const accountNumber = document.getElementById('deposit-account-number').value;
    const amount = parseFloat(document.getElementById('deposit-amount').value);

    try {
        const response = await fetch(`http://127.0.0.1:8000/accounts/${accountNumber}/deposit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: amount }),
        });
        const result = await response.json();
        
        depositResponseMessageDiv.style.display = 'block';
        if (response.ok) {
            depositResponseMessageDiv.className = 'success';
            depositResponseMessageDiv.textContent = result.message;
            depositForm.reset();
        } else {
            depositResponseMessageDiv.className = 'error';
            depositResponseMessageDiv.textContent = `Gagal! ${result.detail}`;
        }
    } catch (error) {
        depositResponseMessageDiv.style.display = 'block';
        depositResponseMessageDiv.className = 'error';
        depositResponseMessageDiv.textContent = 'Error! Tidak dapat terhubung ke server.';
    }
});


// === LOGIKA UNTUK FORM TRANSFER ===
const transferForm = document.getElementById('transfer-form');
const transferResponseMessageDiv = document.getElementById('transfer-response-message');

transferForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const fromAccount = document.getElementById('transfer-from-account').value;
    const toAccount = document.getElementById('transfer-to-account').value;
    const amount = parseFloat(document.getElementById('transfer-amount').value);

    try {
        const response = await fetch(`http://127.0.0.1:8000/accounts/${fromAccount}/transfer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: amount,
                target_account_number: toAccount
            }),
        });
        const result = await response.json();
        
        transferResponseMessageDiv.style.display = 'block';
        if (response.ok) {
            transferResponseMessageDiv.className = 'success';
            transferResponseMessageDiv.textContent = result.message;
            transferForm.reset();
        } else {
            transferResponseMessageDiv.className = 'error';
            transferResponseMessageDiv.textContent = `Gagal! ${result.detail}`;
        }
    } catch (error) {
        transferResponseMessageDiv.style.display = 'block';
        transferResponseMessageDiv.className = 'error';
        transferResponseMessageDiv.textContent = 'Error! Tidak dapat terhubung ke server.';
    }
});