# 📋 Alur Project YouTube Comment Grabber

## 🎯 Tujuan Project
Sistem untuk mengambil live chat dari YouTube livestream, mengelolanya melalui admin dashboard, dan menampilkannya di OBS (Open Broadcaster Software) secara real-time.

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐
│  YouTube Live   │
│   Chat API      │
└────────┬────────┘
         │
         │ (1) Fetch setiap 30 detik
         ▼
┌─────────────────────────────┐
│  poll_live_streams.py       │
│  (Background Process)       │
│  - Auto-detect stream baru  │
│  - Fetch chat messages      │
│  - Store ke database        │
└────────┬────────────────────┘
         │
         │ (2) Simpan ke DB
         ▼
┌─────────────────────────────┐
│      Database               │
│  - LiveStream (streams)     │
│  - LiveChatMessage (chats)  │
└────────┬────────────────────┘
         │
         ├───────────────────┐
         │                   │
         │ (3a) Admin        │ (3b) Public
         ▼                   ▼
┌──────────────────┐   ┌──────────────────┐
│ Admin Dashboard  │   │   OBS Display    │
│ localhost:8000/  │   │ localhost:8000/  │
│ admin/messages/  │   │     display/     │
│                  │   │                  │
│ - Filter chat    │   │ - Auto-update    │
│ - Mark display   │   │ - Rotasi chat    │
│ - Manage order   │   │ - Avatar + Text  │
└──────────────────┘   └──────────────────┘
```

---

## 🚀 Cara Kerja Step-by-Step

### 1️⃣ Setup & Menambah Stream Baru
1. Jalankan server Django: `python manage.py runserver`
2. Login ke admin: `http://localhost:8000/admin/login/`
3. Tambah livestream baru di menu **Live Streams**
   - Masukkan **Video ID** dari YouTube
   - Set **is_active** = ON
   - Atur **display_rotation_seconds** (default: 15 detik)

### 2️⃣ Mengambil Live Chat dari YouTube
1. Jalankan command polling (di terminal terpisah):
   ```bash
   python manage.py poll_live_streams --loop
   ```
2. Command ini akan:
   - ✅ Cek database setiap **30 detik**
   - ✅ Auto-detect stream baru yang ditambahkan admin
   - ✅ Fetch live chat dari YouTube API
   - ✅ Simpan ke database secara otomatis

**Opsi Command:**
```bash
# Default (30 detik interval)
python manage.py poll_live_streams --loop

# Custom interval (15 detik - lebih cepat)
python manage.py poll_live_streams --loop --interval 15

# Hanya untuk video tertentu
python manage.py poll_live_streams --loop --video-id xxxxx
```

### 3️⃣ Mengelola Chat di Admin Dashboard
1. Buka: `http://localhost:8000/admin/messages/`
2. Fitur yang tersedia:
   - **Filter** by status, stream, display
   - **Search** by author atau message
   - **Bulk action** untuk multiple messages
   - **Toggle display** (ON/OFF) untuk setiap message
   - **Auto-update**: Halaman auto-refresh ketika ada message baru

**Status Message:**
- 🔵 **New**: Chat baru masuk
- 🟡 **Reviewed**: Sudah direview
- 🟢 **Sent**: Sudah dikirim/ditampilkan
- 🔴 **Ignored**: Diabaikan

### 4️⃣ Menampilkan di OBS
1. Pilih chat yang mau ditampilkan dengan klik tombol **Display ON**
2. Buka OBS dan tambah **Browser Source**
3. Set URL: `http://localhost:8000/display/`
4. Recommended settings:
   - Width: 1920
   - Height: 1080
   - Tick: ✅ Shutdown source when not visible
   - Tick: ✅ Refresh browser when scene becomes active

**Fitur Display:**
- ✅ **Auto-update** setiap 3 detik (detect message baru/hapus)
- ✅ **Auto-rotate** chat sesuai display_rotation_seconds
- ✅ **Avatar + Username + Message**
- ✅ **Double border** (merah dalam, putih luar)

### 5️⃣ Mengatur Urutan Display
1. Buka: `http://localhost:8000/manage/`
2. Drag & drop untuk mengatur urutan tampilan
3. Atur rotation seconds (berapa detik per chat)
4. Perubahan langsung terdeteksi di OBS display

---

## 📁 Struktur File Penting

```
Youtube-Comment-Grabber/
│
├── manage.py                           # Django management
├── requirements.txt                    # Python dependencies
├── client_secret.json                  # YouTube API credentials
├── youtube_token.json                  # YouTube API token
│
├── dashboard/                          # Django project settings
│   ├── settings.py                     # Konfigurasi utama
│   └── urls.py                         # URL routing utama
│
├── comments/                           # Main app
│   ├── models.py                       # Database models
│   │   ├── LiveStream                  # Model untuk stream
│   │   └── LiveChatMessage             # Model untuk chat
│   │
│   ├── views.py                        # Public views (display, API)
│   ├── admin_views.py                  # Admin dashboard views
│   ├── urls.py                         # URL routing
│   │
│   ├── services/
│   │   ├── youtube.py                  # YouTube API integration
│   │   └── ingest.py                   # Data processing
│   │
│   └── management/commands/
│       ├── poll_live_streams.py        # ⭐ Command polling chat
│       └── fetch_live_chat.py          # Alternative fetch
│
└── templates/
    ├── admin/                          # Admin templates
    │   ├── dashboard.html
    │   ├── livestream_list.html
    │   └── livechatmessage_list.html   # ⭐ Chat management
    │
    └── comments/
        ├── obs_display.html            # ⭐ OBS browser source
        └── manage_display.html         # Display ordering
```

---

## 🔄 Flow Data Real-Time

### Alur Complete dari YouTube → OBS:

1. **YouTube** → `poll_live_streams.py` (setiap 30 detik)
   - Fetch live chat via YouTube API
   
2. `poll_live_streams.py` → **Database**
   - Store chat messages
   - Update stream metadata
   
3. **Admin** → Database
   - Mark chat untuk display (display_selected = True)
   - Set display_order
   
4. **Database** → OBS Display (setiap 3 detik polling)
   - API endpoint: `/api/display_messages/`
   - Return messages dengan display_selected = True
   - Auto-rotate berdasarkan display_rotation_seconds

---

## ⚙️ Konfigurasi Penting

### Database Models:

**LiveStream:**
- `video_id` - ID video YouTube
- `title` - Judul stream
- `is_active` - Stream aktif atau tidak
- `display_rotation_seconds` - Durasi tampil per chat (default: 15)
- `next_page_token` - Token untuk pagination YouTube API
- `last_polled_at` - Terakhir fetch chat

**LiveChatMessage:**
- `message_id` - ID chat dari YouTube
- `live_stream` - Relasi ke LiveStream
- `author_name` - Nama pengirim
- `author_profile_image_url` - Avatar pengirim
- `message_text` - Isi chat
- `status` - Status (new/reviewed/sent/ignored)
- `display_selected` - Ditampilkan di OBS atau tidak
- `display_order` - Urutan tampil

### API Endpoints:

| Endpoint | Method | Fungsi | Auth |
|----------|--------|--------|------|
| `/api/display_messages/` | GET | Get chat untuk OBS display | Public |
| `/api/manage/messages/` | GET | Get chat untuk manage page | Login |
| `/api/manage/reorder/` | POST | Update urutan display | Login |
| `/api/manage/update_rotation/` | POST | Update rotation seconds | Login |
| `/admin/livestreams/` | GET | List streams (+ JSON via AJAX) | Login |
| `/admin/messages/` | GET | Chat management page | Login |

---

## 🎨 Customization OBS Display

File: `templates/comments/obs_display.html`

**Avatar:**
```css
.avatar {
  width: 130px;          /* Ukuran avatar */
  height: 130px;
  border: 3px solid #e1251b;      /* Border dalam (merah) */
  box-shadow: 0 0 0 3px #ffffff;  /* Border luar (putih) */
}
```

**Card Comment:**
```css
.card {
  height: 100px;         /* Tinggi card */
  min-width: 400px;      /* Lebar minimum */
  background: #ffffff;   /* Warna background */
}
```

**Author Name:**
```css
.author {
  font-size: 1.8rem;     /* Ukuran font nama */
  color: #d81e0e;        /* Warna merah */
}
```

**Message:**
```css
.message {
  font-size: 1.2rem;     /* Ukuran font pesan */
  -webkit-line-clamp: 2; /* Maksimal 2 baris */
}
```

---

## 🔧 Troubleshooting

### Chat tidak masuk otomatis?
- ✅ Cek `poll_live_streams.py` masih running
- ✅ Cek stream `is_active = True`
- ✅ Cek YouTube API credentials di `client_secret.json`
- ✅ Cek log error di terminal

### Display OBS tidak update?
- ✅ Refresh browser source di OBS
- ✅ Cek ada chat dengan `display_selected = True`
- ✅ Buka console browser (F12) untuk cek error
- ✅ Test API: `http://localhost:8000/api/display_messages/`

### Admin page tidak auto-update?
- ✅ Cek console browser untuk error JavaScript
- ✅ Pastikan Django server running
- ✅ Clear browser cache

### Stream baru tidak terdeteksi?
- ✅ Wait maksimal 30 detik (interval polling)
- ✅ Cek stream `is_active = True`
- ✅ Restart `poll_live_streams.py` jika perlu

---

## 📝 Workflow Lengkap Penggunaan

1. **Persiapan:**
   ```bash
   # Terminal 1: Django server
   python manage.py runserver
   
   # Terminal 2: Polling chat
   python manage.py poll_live_streams --loop
   ```

2. **Tambah Stream:**
   - Login admin → Live Streams → Add Stream
   - Masukkan Video ID → Save
   - Wait 30 detik, chat mulai masuk otomatis

3. **Pilih Chat untuk Display:**
   - Chat Messages → Centang/pilih chat
   - Klik "Display ON" atau bulk action "Mark for Display"
   - Atau manage order di `/manage/`

4. **Setup OBS:**
   - Add Browser Source
   - URL: `http://localhost:8000/display/`
   - Chat akan auto-rotate dan auto-update

5. **Monitor:**
   - Admin page auto-refresh saat ada chat baru
   - OBS display auto-update setiap 3 detik
   - Background polling auto-detect stream baru

---

## 🎯 Fitur Utama

### ✨ Auto-Update System
- **OBS Display**: Polling 3 detik, auto-detect message baru/hapus
- **Admin Page**: Polling 5 detik, auto-refresh saat ada data baru
- **Polling Command**: Default 30 detik, auto-detect stream baru

### 🎨 Customizable Display
- Avatar size & border (double layer)
- Font size & colors
- Rotation timing per stream
- Card layout & spacing

### 🛠️ Admin Features
- Filter by status, stream, display
- Search by author/message
- Bulk actions (select multiple)
- Drag & drop ordering
- Real-time updates

---

## 📌 Tips & Best Practices

1. **Untuk Performa Optimal:**
   - Set interval polling sesuai kebutuhan (15-60 detik)
   - Jangan terlalu banyak message dengan display_selected=True
   - Hapus message lama secara berkala

2. **Untuk Tampilan Terbaik:**
   - Test di OBS preview dulu sebelum live
   - Adjust font size sesuai resolusi stream
   - Use contrasting colors untuk readability

3. **Untuk Keamanan:**
   - Jangan expose admin dashboard ke public
   - Keep `client_secret.json` private
   - Gunakan strong password untuk admin

---

**🎉 Happy Streaming!**

Untuk pertanyaan atau issue, cek console log di browser/terminal untuk debugging.
