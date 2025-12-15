# YouTube Live Comment Dashboard (Laravel)

Dashboard admin sederhana untuk mengelola daftar live stream YouTube yang ingin dipantau serta meninjau pesan live chat yang sudah ditarik oleh worker terpisah. Aplikasi ini hanya fokus pada workflow internal (belum ada autentikasi publik) sehingga bisa langsung dipasang di jaringan internal tim.

## Fitur Saat Ini

-   CRUD data `LiveStream` termasuk status aktif/nonaktif dan interval polling.
-   Daftar pesan live chat lengkap dengan filter per stream, status, dan pencarian teks.
-   Update status dan catatan pesan secara inline (mis. tandai `sent`, `reviewed`, dll.).
-   Navigasi admin bernuansa gelap sederhana tanpa dependensi UI tambahan.

> **Catatan**: Modul penarik komentar (integrasi YouTube API) akan dijalankan sebagai worker/command terpisah. Dashboard ini sudah menyediakan tabel dan relasi yang dibutuhkan.

## Prasyarat

-   PHP 8.2+
-   Composer 2+
-   Node.js 18+ dan npm (untuk Vite assets)
-   SQLite (default) atau database lain yang didukung Laravel
-   Google API Credentials (OAuth Client) jika ingin menghubungkan worker dengan YouTube Data API

## Setup Cepat

1. **Install dependensi PHP**
    ```bash
    composer install
    ```
2. **Install dependensi frontend** (opsional bila ingin menjalankan Vite dev server)
    ```bash
    npm install
    npm run build # atau npm run dev untuk pengembangan
    ```
3. **Salin env & generate app key**
    ```bash
    copy .env.example .env
    php artisan key:generate
    ```
4. **Konfigurasi database**
    - Default `.env` menggunakan SQLite. Pastikan file `database/database.sqlite` tersedia (buat file kosong bila belum ada).
    - Sesuaikan kredensial jika ingin memakai MySQL/PostgreSQL.
5. **Migrasi schema**
    ```bash
    php artisan migrate
    ```

## Menjalankan Aplikasi

```bash
php artisan serve
```

Laravel akan tersedia di `http://127.0.0.1:8000`. Semua halaman admin bisa diakses lewat:

-   `/admin/live-streams`
-   `/admin/live-chat-messages`

Tidak ada middleware otentikasi bawaan, jadi lindungi aplikasi melalui VPN, Basic Auth, atau reverse proxy sesuai kebutuhan.

## Konfigurasi Worker YouTube (Opsional)

Walau belum termasuk di repo ini, worker pengambil komentar membutuhkan input berikut yang bisa Anda definisikan di `.env` untuk konsistensi:

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/callback
YOUTUBE_SCOPES="https://www.googleapis.com/auth/youtube.force-ssl"
```

Worker tersebut bisa membaca tabel `live_streams` untuk mengetahui video mana yang perlu dipantau, lalu menyimpan pesan ke tabel `live_chat_messages` agar langsung muncul di dashboard.

## Pengembangan Lanjutan

-   Tambahkan autentikasi (mis. Laravel Breeze, Fortify) sebelum dipasang di lingkungan publik.
-   Bungkus aksi update/hapus dengan policy/permission bila ada multi user.
-   Jadwalkan command/artisan untuk polling otomatis dan tandai `sent_at` ketika pesan berhasil diteruskan ke sistem downstream.
-   Tambahkan notifikasi webhook atau integrasi Slack apabila status tertentu tercapai.

## Lisensi

Proyek ini berada di bawah lisensi MIT seperti bawaan Laravel. Lihat file `LICENSE` untuk detailnya.
