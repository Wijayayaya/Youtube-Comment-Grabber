-   Use this file to keep workspace-specific guidance in sync.
-   [ ] Verify that the copilot-instructions.md file in the .github directory is created.

-   [ ] Clarify Project Requirements

    -   Ask for project type, language, and frameworks if not specified. Skip if already provided.

-   [ ] Scaffold the Project

    -   Pastikan langkah sebelumnya selesai.
    -   Gunakan project setup tool (projectType) bila tersedia.
    -   Jalankan perintah scaffolding di direktori kerja saat ini (`.`).
    -   Bila tidak ada template cocok, buat struktur secara manual dengan tool file creation.

-   [ ] Customize the Project

    -   Pastikan langkah sebelumnya ditandai selesai.
    -   Buat rencana perubahan sesuai kebutuhan user.
    -   Terapkan modifikasi memakai tool yang tepat. Lewati hanya untuk proyek "Hello World".

-   [ ] Install Required Extensions

    -   Hanya install extension yang disebut oleh get_project_setup_info. Jika tidak ada, tandai sebagai selesai tanpa instalasi.

-   [ ] Compile the Project

    -   Pastikan dependensi terpasang dan jalankan diagnosa/tes sesuai petunjuk di markdown proyek.

-   [ ] Create and Run Task

    -   Setelah langkah sebelumnya selesai, cek apakah perlu tasks.json (lihat dokumentasi VS Code). Jika perlu, buat memakai create_and_run_task.

-   [ ] Launch the Project

    -   Jalankan hanya setelah user mengonfirmasi mode debug/launch yang diinginkan.

-   [ ] Ensure Documentation is Complete
    -   Pastikan README.md dan file instruksi ini berisi info terbaru.
    -   Tidak boleh ada komentar HTML tersisa di file ini.

## Execution Guidelines

-   Gunakan todo list tool bila tersedia dan perbarui status setiap langkah.
-   Hindari output bertele-tele; ringkas namun informatif.
-   Jangan jelaskan struktur proyek kecuali diminta.

## Development Rules

-   Selalu bekerja di direktori saat ini (`.`) kecuali user menentukan lain.
-   Jangan menambah media/tautan tidak perlu.
-   Gunakan placeholder hanya dengan catatan bahwa harus diganti.
-   Tool VS Code API hanya untuk proyek extension.
-   Setelah proyek dibuat, anggap sudah terbuka di VS Code.

## Folder Creation Rules

-   Jangan membuat folder baru selain jika diminta atau `.vscode` untuk tasks.
-   Pakai perintah yang eksplisit menyasar direktori kerja saat ini saat menjalankan command shell.

## Extension Installation Rules

-   Ikuti hanya rekomendasi dari get_project_setup_info.

## Project Content Rules

-   Jika user belum spesifik, default ke proyek "Hello World".
-   Jangan tambahkan integrasi eksternal tanpa permintaan eksplisit.
-   Semua komponen harus punya kegunaan jelas dalam alur kerja user.
-   Tanyakan klarifikasi bila ada fitur yang belum pasti.

## Task Completion Rules

-   Selesai bila: scaffolding sukses, proyek bisa dikompilasi, README serta file instruksi ini mutakhir, dan user mendapat arahan menjalankan/debug.
-   Selalu perbarui progres sebelum memulai langkah baru.
