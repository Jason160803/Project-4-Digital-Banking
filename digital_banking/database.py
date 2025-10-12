from datetime import date
accounts_db = {}

transactions_db = {}

def reset_daily_limits_if_new_day(account_number: str):
    """Resets the daily transaction count if the last transaction was on a different day."""
    if account_number in accounts_db:
        account = accounts_db[account_number]
        
        # Menggunakan date.today() untuk mendapatkan tanggal hari ini
        today = date.today()

        last_transaction_date = account.get('last_transaction_date')
        
        if last_transaction_date != today:
            account['daily_transaction_count'] = 0
            account['last_transaction_date'] = today