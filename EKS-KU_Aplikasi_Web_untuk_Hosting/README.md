---
title: EKS-KU Pendaftaran Ekstrakurikuler
emoji: 🌿
colorFrom: green
colorTo: emerald
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# EKS-KU — Pendaftaran Ekstrakurikuler Sekolah

Aplikasi pendaftaran ekstrakurikuler dengan tema hijau daun.

- Hanya siswa kelas 10 dan 11 yang boleh mendaftar.
- Pilihan: Drumband, Pramuka, Rohis, Multimedia, Pasbrana, Olahraga, PMR, KIR, Seni.
- Mencegah pendaftaran ganda berdasarkan NIS.
- Bukti pendaftaran dan rekap CSV.

**Catatan:** Versi ini menggunakan SQLite. Pada hosting gratis tertentu, file lokal dapat terhapus saat ruang aplikasi dibangun ulang atau tidur. Untuk data resmi jangka panjang, gunakan database persisten dan lindungi menu admin dengan autentikasi.
