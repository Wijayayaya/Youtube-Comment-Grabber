# YouTube Live Chat Dashboard

Dashboard berbasis Django untuk mengambil komentar live YouTube via API dan mengelolanya sebelum dikirim ke sistem lain. Proyek ini menyediakan:

- Pengambilan live chat menggunakan OAuth (scope `youtube.force-ssl`).
- Penyimpanan pesan ke database dengan status workflow (baru, ditinjau, terkirim, diabaikan).
- Dashboard web untuk memfilter, memberi catatan, dan memperbarui status komentar.
- Endpoint API sederhana agar layanan eksternal dapat menarik pesan dan menandai yang sudah diproses.

## Prasyarat

- Python 3.10 atau lebih baru.
- Akun Google Cloud dengan YouTube Data API v3 aktif dan kredensial OAuth tipe _Desktop App_.
- Windows PowerShell (atau shell lain yang kompatibel) untuk menjalankan perintah.

## Konfigurasi Awal

1. **Siapkan variabel lingkungan**

   - Salin `.env.example` menjadi `.env` lalu isi nilai yang sesuai.
   - `DJANGO_SECRET_KEY` bisa berupa string acak untuk penggunaan lokal.
   - `YOUTUBE_CLIENT_SECRET` menunjuk pada file JSON OAuth yang diunduh dari Google Cloud Console.

2. **Instal dependensi Python**

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. **Jalankan migrasi database**

   ```powershell
   python manage.py migrate
   ```

4. **(Opsional) Buat superuser untuk akses /admin**

   ```powershell
   python manage.py createsuperuser
   ```

## Mengambil Live Chat

Gunakan salah satu dari dua perintah berikut:

### 1. Single live berdasarkan ID (cepat)

Saat pertama menjalankan, browser akan terbuka untuk proses OAuth dan token akan disimpan di `youtube_token.json`.

```powershell
python manage.py fetch_live_chat --video-id=<ID_VIDEO_LIVE> --loop
```

- Hilangkan `--loop` jika hanya ingin mengambil satu batch pesan.
- Gunakan `--max-iterations=<n>` untuk membatasi jumlah polling saat `--loop` aktif.

Perintah ini mengisi tabel `LiveChatMessage` dengan status awal `new`.

### 2. Live berdasarkan data di admin (otomatis banyak video)

Tambahkan entri `LiveStream` via Django Admin dan centang `is_active`. Setelah itu jalankan:

```powershell
python manage.py poll_live_streams --loop
```

- Tanpa argumen ia memproses seluruh `LiveStream` aktif. Batasi dengan `--video-id=<ID>` (bisa lebih dari sekali).
- Ubah interval antar siklus dengan `--interval=10` (detik).
- Gunakan `--refresh-metadata` bila ingin memaksa update judul/live chat ID setiap siklus.

## Menjalankan Dashboard

1. Start server Django:

   ```powershell
   python manage.py runserver
   ```

2. Buka `http://127.0.0.1:8000/`; alamat ini sekarang mengarahkan langsung ke `/admin/` dan tidak menampilkan daftar komentar sendiri.

3. Kelola komentar lewat antarmuka Django Admin (`/admin/`).

## Integrasi ke Sistem Lain

API sederhana tersedia bagi pengguna yang sudah login ke Django (session/cookie auth). Pastikan masuk ke `/admin/` dengan akun valid lalu gunakan endpoint berikut jika perlu otomatisasi internal:

- `GET /api/messages/?status=new&limit=50` — Ambil pesan terbaru sesuai filter (opsional `video_id`, `since` ISO datetime).
- `POST /api/messages/<pk>/mark-sent/` — Tandai pesan telah dikirim. Kirim field `note` jika ingin menyimpan catatan.

Contoh memakai PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/messages/?status=new" -Method Get
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/messages/12/mark-sent/" -Method Post -Body @{ note = "Sudah dikirim ke CRM" }
```

## Tips

- Pastikan video yang dipantau memang live dan chat tidak dimatikan; jika tidak, API akan mengembalikan error `commentsDisabled`.
- Jika izin OAuth berubah, hapus `youtube_token.json` untuk memaksa login ulang.
- Gunakan scheduler (Task Scheduler, cron, dll.) untuk menjalankan `fetch_live_chat` secara berkala selama live berlangsung.
