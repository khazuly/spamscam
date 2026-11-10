# SpamScam (Optimized Edition)

Tool pengujian OTP multi-provider dengan arsitektur konkuren (paralel), connection pooling, responsivitas tinggi, dan pelaporan statistik real-time.

## Fitur & Optimasi Terbaru

- ⚡ **Eksekusi Paralel (Multithreading):** Seluruh provider dieksekusi secara konkuren (`ThreadPoolExecutor`), memangkas waktu tunggu per siklus hingga 5x–10x lebih cepat.
- 🔄 **HTTP Connection Pooling & Keep-Alive:** Menggunakan `requests.Session` dan adapter connection pool untuk mengeliminasi overhead handshake TCP/TLS berulang.
- 🎯 **Optimasi Slider Template Matching (AdaKami):** Pemotongan kanvas vertikal terfokus pada koordinat target sebelum template matching, menghemat penggunaan CPU OpenCV secara signifikan.
- 🛡️ **Network Resilience & Safe Timeouts:** Timeout koneksi adaptif `(5s connect, 15s read)` mencegah thread macet jika salah satu server tujuan down/lambat.
- 💻 **Mendukung Mode CLI & Interaktif:** Dapat dijalankan via interactive prompt biasa atau melalui argumen command-line (`--phone`, `--count`, `--workers`, dll.) untuk otomatisasi.
- 📊 **Statistik & Telemetri:** Menampilkan waktu latensi (durasi) per provider secara real-time serta ringkasan total keberhasilan di akhir siklus.

## Provider yang Didukung

- **AdaKami** (Slider CAPTCHA solver)
- **Indosaku** (Enkripsi AES-ECB)
- **KrediOne** (HMAC/MD5 signature)
- **RupiahCepat** (Enkripsi AES-CBC)
- **KreditNavigator** (Enkripsi AES-CBC)
- **HRS-BRE** (Form multipart carrier)
- **Dunia Games** (WhatsApp/SMS OTP)
- **Bonus Belanja** (Registration API)

## Instalasi

Install dependensi yang dibutuhkan:

```bash
pip install -r requirements.txt
```

## Penggunaan

### 1. Mode Interaktif (Bawaan)

Jalankan script langsung:

```bash
python main.py
```

Anda akan diminta memasukkan nomor HP target (contoh: `08978397772`) dan jumlah siklus resend.

### 2. Mode Command Line (CLI)

Anda juga dapat menjalankan langsung dengan argumen untuk kemudahan otomatisasi:

```bash
# Jalankan 3 siklus ke nomor target secara paralel (default 5 worker)
python main.py -p 08978397772 -c 3

# Tentukan cooldown kustom (contoh: 30 detik) dan jumlah worker
python main.py -p 08978397772 -c 5 -d 30 -w 5

# Hanya jalankan provider tertentu
python main.py -p 08978397772 -c 1 --providers Indosaku,RupiahCepat

# Jalankan dalam mode sekuensial (jika ingin tanpa paralelisme)
python main.py -p 08978397772 -c 2 --sequential
```

#### Opsi Argumen CLI

| Argumen | Deskripsi | Default |
|---|---|---|
| `-p`, `--phone` | Nomor HP target (`08xxxxxxxxxx`) | Interaktif |
| `-c`, `--count` | Jumlah siklus pengiriman | Interaktif |
| `-d`, `--cooldown` | Durasi jeda antar siklus (detik) | `62` |
| `-w`, `--workers` | Jumlah thread worker paralel | `5` |
| `--providers` | Filter provider (pisahkan koma) | Semua |
| `--sequential` | Paksa mode eksekusi sekuensial | `False` |

## Struktur Proyek

```
spamscam/
├── main.py                          # Entry point CLI (paralel & interaktif)
├── requirements.txt                 # Daftar pustaka Python
├── README.md                        # Dokumentasi proyek
└── provider/
    ├── __init__.py                  # Registri provider & backward-compatible exports
    ├── base.py                      # Model ProviderResult, Session builder & pooling
    ├── utils.py                     # Helper user agent, formatting, & multipart
    ├── adakami_provider.py          # Provider AdaKami (optimized slider matcher)
    ├── indosaku_provider.py         # Provider Indosaku (AES-ECB)
    ├── kredione_provider.py         # Provider KrediOne (MD5 signature)
    ├── rc_provider.py               # Provider RupiahCepat (AES-CBC)
    ├── kreditnavigator_provider.py  # Provider KreditNavigator (AES-CBC + session reuse)
    ├── hrsbre_provider.py           # Provider HRS-BRE (multipart form)
    ├── duniagames_provider.py       # Provider Dunia Games (send-otp)
    └── bonusbelanja_provider.py     # Provider Bonus Belanja (registration app)
```
