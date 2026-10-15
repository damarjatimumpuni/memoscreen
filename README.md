# Status Screen Saver

Aplikasi desktop ringan berbasis Python/Tkinter untuk Windows 10/11 yang
menampilkan pesan status besar dalam mode layar penuh — misalnya
**SEDANG SHOLAT**, **SEDANG RAPAT**, atau **JANGAN DIGANGGU** — agar
rekan kerja dapat melihat status pengguna.

> Catatan: ini adalah aplikasi fullscreen biasa, bukan screensaver
> Windows (`.scr`).

## Fitur

- 10 preset status (mudah diedit di `presets.py`)
- Pesan kustom bebas; jika diisi, pesan kustom menggantikan preset
- 6 warna latar dan 4 warna teks (swatch)
- Jam digital `HH:MM` opsional, diperbarui tiap detik via `after()`
- Ukuran teks otomatis menyesuaikan panjang pesan dan resolusi layar
- Keluar dengan `ESC` atau tombol **Stop**
- Preferensi tersimpan di `%APPDATA%\StatusScreenSaver\config.json`
- Tanpa koneksi internet, tanpa dependensi pihak ketiga

## Persyaratan

- Windows 10/11
- Python 3.11 atau lebih baru (Tkinter sudah termasuk dalam instalasi standar)

## Cara menjalankan

```bash
python main.py
```

## Cara memakai

1. Pilih status pada dropdown **Status**.
2. Opsional: ketik **Pesan Kustom**. Jika tidak kosong, pesan inilah yang
   ditampilkan.
3. Klik swatch **Warna Latar** dan **Warna Teks**.
4. Centang **Tampilkan jam digital** bila diperlukan.
5. Klik **Mulai**.

Untuk keluar dari mode layar penuh:

- Tekan `ESC`, atau
- `Alt+Tab` ke window kontrol lalu klik **Stop** (window layar penuh
  menutupi seluruh monitor, sehingga window kontrol hanya dapat dijangkau
  lewat `Alt+Tab`).

## Konfigurasi

Preferensi (status terakhir, pesan kustom, warna, preferensi jam)
disimpan otomatis di:

```
%APPDATA%\StatusScreenSaver\config.json
```

File yang hilang atau rusak tidak menyebabkan aplikasi gagal — nilai
bawaan akan dipakai.

## Membuat executable Windows

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name StatusScreenSaver main.py
```

Hasilnya ada di `dist\StatusScreenSaver.exe`. Tidak memerlukan hak akses
administrator dan tidak mengubah registry maupun pengaturan sistem.

## Pengujian

Uji coba otomatis (tanpa perlu tampilan grafis):

```bash
python -m unittest discover -s tests -v
```

Uji coba manual yang harus dilakukan di Windows:

1. Window kontrol terbuka normal.
2. Semua preset status tersedia di dropdown.
3. Pesan kustom ditampilkan saat diisi.
4. Pesan kosong ditolak (indikator menampilkan penjelasan).
5. Window layar penuh menutupi monitor utama.
6. Teks berada di tengah dan ukurannya menyesuaikan.
7. Semua warna latar berfungsi.
8. Jam digital berjalan dan berhenti saat window ditutup.
9. `ESC` menutup mode layar penuh.
10. Tombol **Stop** menutup mode layar penuh.
11. Aplikasi tetap terbuka setelah mode layar penuh ditutup.
12. Mode layar penuh dapat dibuka berulang kali tanpa error.
13. Preferensi tetap tersimpan setelah aplikasi dibuka kembali.
14. File konfigurasi rusak/hilang tidak menyebabkan crash.
15. Aplikasi berjalan tanpa internet.
16. Aplikasi dapat dikemas menjadi executable.

## Struktur proyek

```
status-screen-saver/
├── main.py          # Titik masuk dan window kontrol
├── presets.py       # Preset status dan warna
├── config.py        # Muat/simpan preferensi JSON
├── fullscreen.py    # Window layar penuh, ukuran teks adaptif, jam
├── styles.py        # Gaya visual bersama
├── tests/           # Uji coba headless (unittest)
├── requirements.txt
└── README.md
```

## Keterbatasan

- Hanya menargetkan monitor utama (dukungan multi-monitor dapat
  ditambahkan kemudian).
- Tombol **Stop** memerlukan `Alt+Tab` karena window layar penuh
  menutupi seluruh monitor; `ESC` adalah cara tercepat keluar.
- Tidak ada instalasi otomatis, perubahan registry, maupun auto-start.
