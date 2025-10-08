# app/data.py

from datetime import datetime, date

# Asumsi: Setiap nasabah diidentifikasi oleh nomor rekening unik.
# Kita akan gunakan dictionary di mana key adalah nomor rekening (string).

accounts = {}
# Contoh struktur 'accounts':
# {
#     "1122334455": {
#         "account_number": "1122334455",
#         "name": "Budi Santoso",
#         "bank_name": "Bank Digital",
#         "balance": 500000.0,
#         "is_active": True
#     }
# }

transactions = {}
# Contoh struktur 'transactions':
# {
#     "1122334455": [
#         {
#             "type": "deposit",
#             "amount": 100000.0,
#             "timestamp": "2025-10-15T10:00:00"
#         }
#     ]
# }

# Batasan transaksi harian
daily_transaction_limits = {}
# Contoh struktur 'daily_transaction_limits':
# {
#     "1122334455": {
#         "date": date(2025, 10, 15),
#         "count": 1
#     }
# }

# Pengaturan Sistem (dapat dianggap sebagai konstanta)
MINIMUM_BALANCE = 50000.0
INTER_BANK_TRANSFER_FEE = 6500.0
MAX_TRANSFER_AMOUNT = 25000000.0
MAX_DAILY_TRANSACTIONS = 10