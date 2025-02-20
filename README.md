# Rekomendasi Jurusan & Kampus

Aplikasi ini membantu pengguna mendapatkan rekomendasi jurusan dan kampus berdasarkan profil pribadi mereka.

## 🛠 Fitur Utama
- Input data pengguna melalui formulir
- Menggunakan OpenAI untuk menghasilkan rekomendasi
- Menampilkan rekomendasi dalam format tabel
- Menyediakan opsi untuk mengunduh rekomendasi dalam format PDF

## 🚀 Cara Menjalankan Aplikasi

1. **Persiapan**:
   - Pastikan Python sudah terinstal (disarankan versi 3.8+).
   - Install dependensi dengan perintah:
     ```bash
     pip install -r requirements.txt
     ```

2. **Menjalankan Aplikasi**:
   ```bash
   streamlit run app_ori.py
   ```

3. **Konfigurasi API Key OpenAI**:
   - Setel API key OpenAI sebagai variabel lingkungan:
     ```bash
     export OPENAI_API_KEY="your-api-key"
     ```
   - Atau, pada Windows (PowerShell):
     ```powershell
     $env:OPENAI_API_KEY="your-api-key"
     ```

## 📜 Lisensi
Aplikasi ini bersifat open-source dan bebas digunakan untuk tujuan non-komersial.
