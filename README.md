# SpamScam

Tool buat ngebombing OTP. Tiap siklus ngirim request ke semua provider, terus nunggu cooldown 62 detik sebelum lanjut ke siklus berikutnya.

## Provider yang tersedia saat ini

- AdaKami
- Indosaku
- KrediOne
- RupiahCepat
- KreditNavigator
- HRS-BRE
- Dunia Games
- Bonus Belanja

## Cara pakai

Install dulu dependensinya:

```
pip install -r requirements.txt
```

Jalankan:

```
python main.py
```

Nanti bakal diminta input nomor HP target dan berapa kali mau diresend. Masukkan nomor dengan format `08xxxxxxxxxx`.

## Struktur proyek

```
smsOtp/
├── main.py
├── requirements.txt
└── provider/
    ├── __init__.py
    ├── utils.py
    ├── adakami_provider.py
    ├── indosaku_provider.py
    ├── kredione_provider.py
    ├── rc_provider.py
    ├── kreditnavigator_provider.py
    ├── hrsbre_provider.py
    ├── duniagames_provider.py
    └── bonusbelanja_provider.py
```