Deployment notes — systemd services
=================================

Ringkasan langkah untuk meng-deploy release ke server produksi.

1) Salin unit-file systemd

  # Di server produksi (jalankan sebagai root atau pakai sudo)
  sudo cp deploy/systemd/dashboardLive.service /etc/systemd/system/dashboardLive.service
  sudo cp deploy/systemd/pollLive.service /etc/systemd/system/pollLive.service

2) Buat direktori deploy dan shared

  sudo mkdir -p /var/www/youtube_chat_dashboard/releases
  sudo mkdir -p /var/www/youtube_chat_dashboard/shared/media
  sudo mkdir -p /var/www/youtube_chat_dashboard/shared/logs
  sudo chown -R www-data:www-data /var/www/youtube_chat_dashboard

3) Reload systemd dan enable services

  sudo systemctl daemon-reload
  sudo systemctl enable dashboardLive pollLive

4) Menjalankan layanan

  sudo systemctl start dashboardLive
  sudo systemctl start pollLive

5) Melihat log

  sudo journalctl -u dashboardLive -f
  sudo journalctl -u pollLive -f

6) Catatan penting

- Unit-file menggunakan `WorkingDirectory` yang menunjuk ke `/var/www/youtube_chat_dashboard/current`. Pipeline deploy akan
  mengekstrak release ke `releases/<APP>-<BUILD>` dan membuat symlink `current`.
- Buat `shared` untuk file yang harus persist (user-uploaded media, logs). Anda bisa menambahkan langkah pada deploy untuk
  membuat symlink dari `current/media` ke `shared/media` sebelum restart.
- Sesuaikan `User`/`Group` di `deploy/systemd/*.service` sesuai user di server (contoh: `www-data`).
- Untuk production, pertimbangkan menggunakan Gunicorn + nginx alih-alih `manage.py runserver`.

Gunicorn notes
---------------

- `dashboardLive.service` sekarang mengarahkan ke Gunicorn. Pastikan `gunicorn` terinstal di virtualenv (sudah ditambahkan ke `requirements.txt`).
- Jika Anda ingin menambahkan `nginx` di depan Gunicorn, arahkan `nginx` ke `http://127.0.0.1:8000` atau socket unix.
- Contoh systemd unit menggunakan Gunicorn sudah ada di `deploy/systemd/dashboardLive.service`.

Jika mau, saya bisa juga:
- ubah unit-file untuk menggunakan unix socket (`/run/youtube_chat_dashboard.sock`) dan contoh `nginx` config, atau
- tambahkan step di `Jenkinsfile` untuk memastikan `gunicorn` termasuk saat menginstall deps.

7) Contoh: mengaktifkan shared media symlink selama deploy (bash snippet)

  # di dalam step deploy setelah ekstrak release
  mkdir -p "$RELEASE_DIR/shared/media"
  ln -sfn "$DEPLOY_ROOT/shared/media" "$RELEASE_DIR/media"

8) Environment / secrets

- Simpan kredensial di Jenkins Credentials dan ekspor ke environment atau tulis file `.env` di `shared` yang di-link ke `current`.

Jika mau, saya bisa menambahkan task di `Jenkinsfile` untuk meng-copy unit-file otomatis ke server (via `scp`) dan men-enable service.
