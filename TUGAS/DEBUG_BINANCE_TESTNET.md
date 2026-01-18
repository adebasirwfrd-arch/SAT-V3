# DEBUG GUIDE: Binance Testnet API Setup

## Error yang Terjadi
```
❌ ORDER FAILED: binance {"code":-2015,"msg":"Invalid API-key, IP, or permissions for action."}
```

**Penyebab:** API Key di `.env` belum valid atau bukan dari Binance Testnet yang benar.

---

## Langkah-Langkah Debug

### STEP 1: Buka Binance Testnet Portal
1. Buka browser
2. Pergi ke: **https://testnet.binance.vision/**
3. Klik **"Log In with GitHub"** (wajib punya akun GitHub)

### STEP 2: Generate API Keys
1. Setelah login, klik **"Generate HMAC_SHA256 Key"**
2. Masukkan label (contoh: `SAT-V3-Bot`)
3. **PENTING**: Copy kedua key ini:
   - **API Key** (panjang ~64 karakter)
   - **Secret Key** (panjang ~64 karakter)

### STEP 3: Update File .env
Edit file `/Users/izzadev/.gemini/antigravity/scratch/SAT-V3/.env`:

```ini
BINANCE_API_KEY=paste_api_key_dari_testnet_disini
BINANCE_SECRET_KEY=paste_secret_key_dari_testnet_disini
TRADING_MODE=TESTNET
```

### STEP 4: Verifikasi Testnet Balance
1. Di halaman testnet.binance.vision, Anda otomatis dapat saldo gratis:
   - 1,000,000 USDT
   - 1 BTC
   - dll

### STEP 5: Test Koneksi
Jalankan script test ini:
```bash
cd /Users/izzadev/.gemini/antigravity/scratch/SAT-V3
source venv/bin/activate
python -c "
import ccxt
from config.settings import Config

exchange = ccxt.binance({
    'apiKey': Config.API_KEY,
    'secret': Config.SECRET_KEY
})
exchange.set_sandbox_mode(True)

# Test fetch balance
balance = exchange.fetch_balance()
print('✅ Connection SUCCESS!')
print(f'USDT Balance: {balance[\"USDT\"][\"free\"]}')
print(f'BTC Balance: {balance[\"BTC\"][\"free\"]}')
"
```

### STEP 6: Jalankan Bot
```bash
./run_mac_local.sh
```

---

## Checklist Debug

- [ ] Sudah login ke testnet.binance.vision dengan GitHub
- [ ] Sudah generate API Key baru
- [ ] Sudah copy API Key ke file .env
- [ ] Sudah copy Secret Key ke file .env
- [ ] Test koneksi berhasil (Step 5)
- [ ] Bot berjalan tanpa error

---

## Notes Penting

> ⚠️ API Key dari **testnet.binance.vision** BERBEDA dengan:
> - Binance.com (Real/Live)
> - Binance Futures Testnet

Pastikan Anda menggunakan key dari **testnet.binance.vision** (SPOT Testnet).
