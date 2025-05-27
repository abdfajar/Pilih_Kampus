import os
import openai
import streamlit as st
from fpdf import FPDF
import uuid # Untuk nama file audio yang unik

# --- Inisialisasi Klien OpenAI ---
# Pastikan OPENAI_API_KEY sudah diatur di environment variable Anda
# atau di Streamlit secrets jika dideploy.
try:
    client = openai.OpenAI()
    # Tes koneksi ringan untuk memastikan API key valid
    client.models.list(limit=1)
except openai.AuthenticationError as e:
    st.error(
        "Autentikasi OpenAI gagal. Pastikan variabel lingkungan OPENAI_API_KEY Anda sudah diatur dengan benar dan valid. "
        "Jika menggunakan Streamlit Cloud, pastikan sudah diatur di Secrets."
    )
    st.stop() # Hentikan eksekusi jika klien tidak bisa diinisialisasi
except Exception as e:
    st.error(f"Gagal menginisialisasi klien OpenAI: {e}")
    st.stop()

def generate_prompt(profil):
    return (
        f"Berikan rekomendasi 3 jurusan dari 3 kampus sesuai dengan profil berikut ini dan sajikan dalam bentuk tabular "
        f"serta peluang untuk dapat diterima:\n\n{profil}\n\nFormat keluaran yang diharapkan:\n"
        "| Kampus | Jurusan | Peluang Diterima (%) |\n"
        "|--------|---------|--------------------|\n"
        "| ...    | ...     | ...                |\n"
        "| ...    | ...     | ...                |\n"
        "| ...    | ...     | ...                |"
    )

def call_openai_api(prompt_text):
    # Menggunakan klien global yang sudah diinisialisasi
    response = client.chat.completions.create(
        model="gpt-4",  # Pertimbangkan gpt-3.5-turbo untuk kecepatan & biaya jika gpt-4 tidak krusial
        messages=[
            {"role": "system", "content": "Anda adalah asisten yang memberikan rekomendasi jurusan dan kampus dalam format tabel markdown."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7,
        top_p=0.9
    )
    return response.choices[0].message.content

def format_recommendation_for_speech(markdown_table_text):
    """Mengubah tabel markdown rekomendasi menjadi teks yang lebih alami untuk TTS."""
    lines = markdown_table_text.strip().split('\n')
    speakable_parts = []

    if len(lines) < 3: # Header, separator, minimal 1 data
        return "Format rekomendasi tidak sesuai untuk dibacakan."

    # Baris data dimulai dari indeks 2 (setelah header dan separator)
    data_lines = lines[2:]
    
    speakable_parts.append("Berikut adalah rekomendasi jurusan dan kampus untuk Anda:")
    
    for i, line in enumerate(data_lines):
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) == 3:
            kampus, jurusan, peluang = cells[0], cells[1], cells[2]
            # Hapus '%' jika ada dan ganti dengan kata 'persen' untuk pembacaan yang lebih baik
            peluang_text = peluang.replace('%', '').strip() + " persen"
            speakable_parts.append(f"Rekomendasi ke-{i+1}: Kampus {kampus}, jurusan {jurusan}, dengan peluang diterima {peluang_text}.")
        else:
            # Jika ada baris yang tidak sesuai format, lewati atau catat
            print(f"Melewati baris dengan format tidak sesuai: {line}")
            
    if len(speakable_parts) == 1 and len(data_lines) > 0 : # Hanya ada intro, tapi ada data yg gagal parse
        return "Ada beberapa data rekomendasi yang tidak bisa dibacakan karena formatnya. Silakan periksa teks."
    elif len(speakable_parts) == 1: # Tidak ada data yang berhasil diparsing
        return "Tidak ada data rekomendasi yang dapat dibacakan."
        
    return " ".join(speakable_parts)

def generate_and_play_speech(text_to_speak, voice_choice="nova"):
    """Menghasilkan audio dari teks dan menyiapkannya untuk st.audio."""
    temp_audio_filename = f"temp_audio_{uuid.uuid4()}.mp3"
    try:
        # Menggunakan klien global
        response_audio = client.audio.speech.create(
            model="tts-1",          # atau "tts-1-hd" untuk kualitas lebih tinggi
            voice=voice_choice,     # pilihan: alloy, echo, fable, onyx, nova, shimmer
            input=text_to_speak,
            response_format="mp3"
        )
        response_audio.stream_to_file(temp_audio_filename)
        
        with open(temp_audio_filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        st.audio(audio_bytes, format="audio/mp3")
        
    except openai.APIError as e:
        st.error(f"Terjadi kesalahan API OpenAI saat menghasilkan suara: {e}")
    except Exception as e:
        st.error(f"Gagal menghasilkan atau memutar suara: {e}")
    finally:
        # Hapus file audio sementara setelah digunakan
        if os.path.exists(temp_audio_filename):
            try:
                os.remove(temp_audio_filename)
            except Exception as e_del:
                st.warning(f"Gagal menghapus file audio sementara ({temp_audio_filename}): {e_del}")

def save_as_pdf(profil, rekomendasi):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16) # Gunakan font yang mendukung UTF-8 jika perlu
    pdf.cell(200, 10, "Hasil Rekomendasi Jurusan & Kampus", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Profil Pengguna:\n{profil}\n")
    pdf.ln(5)
    
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(0, 10, "Rekomendasi:", ln=True)
    pdf.set_font("Arial", size=12)
    # Untuk PDF, karakter Markdown mungkin perlu di-handle atau teks dibersihkan
    # FPDF multi_cell akan menampilkan teks apa adanya.
    pdf.multi_cell(0, 10, rekomendasi) 
    
    pdf_output_filename = f"rekomendasi_jurusan_{uuid.uuid4()}.pdf"
    pdf.output(pdf_output_filename)
    return pdf_output_filename

def main():
    st.title("📝 Formulir Pemilihan Jurusan & Kampus")
    st.write("Silakan isi formulir berikut untuk mengetahui rekomendasi jurusan dan kampus yang sesuai dengan minat dan potensi Anda.")

    # Inisialisasi session_state jika belum ada
    if 'recommendation_text' not in st.session_state:
        st.session_state.recommendation_text = None
    if 'profil_text' not in st.session_state:
        st.session_state.profil_text = None
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None
    if 'show_success_message' not in st.session_state:
        st.session_state.show_success_message = False


    # === Bagian Formulir (Sama seperti kode Anda) ===
    st.header("📌 Informasi Pribadi")
    nama = st.text_input("Nama Lengkap", key="nama")
    # ... (Sisa input form Anda, pastikan semua memiliki 'key' unik jika ada logika yang bergantung padanya) ...
    # Contoh singkat:
    jenis_kelamin = st.radio("Jenis Kelamin", ("Laki-laki", "Perempuan"), key="jenis_kelamin")
    usia = st.number_input("Usia", min_value=15, max_value=30, step=1, key="usia")
    domisili = st.text_input("Kota/Kabupaten Domisili", key="domisili")
    sekolah = st.text_input("Sekolah Asal", key="sekolah")
    jurusan_sma = st.selectbox("Jurusan SMA", ["IPA", "IPS", "Bahasa", "Lainnya"], key="jurusan_sma")
    nilai_rapor = st.slider("Nilai rata-rata rapor semester terakhir", min_value=0.0, max_value=100.0, step=0.1, key="nilai_rapor")

    st.header("📌 Profil Orang Tua/Wali")
    nama_orangtua = st.text_input("Nama Orang Tua/Wali", key="nama_ortu")
    pekerjaan = st.text_input("Pekerjaan Orang Tua/Wali", key="pekerjaan_ortu")
    pendapatan = st.selectbox("Kisaran Pendapatan per Bulan", ["< Rp3 juta", "Rp3-5 juta", "Rp5-10 juta", "> Rp10 juta"], key="pendapatan_ortu")
    
    st.header("📌 Minat dan Preferensi Akademik")
    mata_pelajaran = st.multiselect(
        "Mata pelajaran favorit", 
        ["Matematika", "Fisika", "Kimia", "Biologi", "Ekonomi", "Sosiologi", "Sejarah", "Bahasa Inggris", "Seni dan Desain", "Teknologi Informasi"],
        key="mapel_fav"
    )
    lingkungan_kerja = st.selectbox("Saya lebih suka bekerja di", ["Kantor", "Lapangan", "Studio Kreatif"], key="lingkungan_kerja")
    karier = st.selectbox("Saya ingin berkarier di bidang", ["Teknologi", "Kesehatan", "Bisnis", "Sosial", "Seni"], key="bidang_karier")
    kerja_tim = st.radio("Saya lebih suka bekerja secara", ["Mandiri", "Tim kecil", "Tim besar"], key="kerja_tim")
    
    st.header("📌 Prospek Karier dan Pengembangan Diri")
    gaji_tinggi = st.slider("Seberapa penting potensi gaji yang tinggi?", 1, 5, 3, key="gaji")
    stabilitas_pekerjaan = st.slider("Seberapa penting stabilitas pekerjaan?", 1, 5, 3, key="stabilitas")
    kesempatan_luar_negeri = st.slider("Seberapa penting kesempatan kerja di luar negeri?", 1, 5, 3, key="luar_negeri")
    fleksibilitas_karier = st.slider("Seberapa penting fleksibilitas karier?", 1, 5, 3, key="fleksibilitas")
    hobi_minat = st.slider("Seberapa penting jurusan sesuai dengan minat pribadi?", 1, 5, 3, key="minat_pribadi")

    st.header("📌 Rekomendasi Kampus")
    jenis_kampus = st.selectbox("Saya lebih tertarik dengan kampus", ["Negeri", "Swasta", "Spesialisasi Tertentu", "Internasional"], key="jenis_kampus")
    faktor_kampus = st.multiselect("Faktor utama dalam memilih kampus", ["Lokasi", "Akreditasi", "Biaya", "Fasilitas", "Beasiswa"], key="faktor_kampus")
    # === Akhir Bagian Formulir ===

    if st.button("Dapatkan Rekomendasi", key="btn_dapatkan_rekomendasi"):
        with st.spinner("Merangkum profil Anda..."):
            profil_ringkas = (
                f"{nama}, seorang {jenis_kelamin} berusia {usia} tahun dari {domisili}, lulusan {sekolah} dengan jurusan {jurusan_sma} "
                f"dan nilai rata-rata {nilai_rapor}. Orang tua/wali, {nama_orangtua}, bekerja sebagai {pekerjaan} dengan pendapatan {pendapatan}. "
                f"Minat akademiknya meliputi {', '.join(mata_pelajaran)} dan lebih suka bekerja di {lingkungan_kerja}. "
                f"Mereka ingin berkarier di bidang {karier} dan lebih suka bekerja dalam {kerja_tim}. Kampus idealnya adalah {jenis_kampus} "
                f"dengan faktor utama {', '.join(faktor_kampus)}."
                f" Dengan mempertimbangkan Prospek Karier dan Pengembangan Diri: "
                f"Potensi Gaji Tinggi: {gaji_tinggi}/5, "
                f"Stabilitas Pekerjaan: {stabilitas_pekerjaan}/5, "
                f"Kesempatan Kerja di Luar Negeri: {kesempatan_luar_negeri}/5, "
                f"Fleksibilitas Karier: {fleksibilitas_karier}/5, "
                f"Kesesuaian dengan Minat Pribadi: {hobi_minat}/5."
            )
            st.session_state.profil_text = profil_ringkas
        
        with st.spinner("Sedang memproses rekomendasi dari AI... Mohon tunggu."):
            prompt = generate_prompt(st.session_state.profil_text)
            api_response = call_openai_api(prompt)
            st.session_state.recommendation_text = api_response
        
        with st.spinner("Menyiapkan PDF..."):
            pdf_path = save_as_pdf(st.session_state.profil_text, st.session_state.recommendation_text)
            st.session_state.pdf_path = pdf_path
        
        st.session_state.show_success_message = True # Tandai untuk menampilkan pesan sukses

    # Tampilkan hasil jika rekomendasi sudah ada di session_state
    if st.session_state.recommendation_text:
        st.subheader("📌 Hasil Rekomendasi")
        if st.session_state.profil_text:
            st.markdown("### 📋 Ringkasan Profil Anda")
            st.markdown(st.session_state.profil_text)
        
        st.markdown("### 🎓 Rekomendasi Jurusan & Kampus")
        st.markdown(st.session_state.recommendation_text, unsafe_allow_html=True) # unsafe_allow_html untuk render tabel Markdown

        st.markdown("---") # Pemisah visual

        # Tombol Suara
        st.markdown("#### Dengarkan Rekomendasi:")
        # Pilihan suara untuk TTS
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        selected_voice = st.selectbox("Pilih Suara:", voice_options, index=voice_options.index("nova"), key="voice_select")

        if st.button("🔊 Putar Suara Rekomendasi", key="btn_putar_suara"):
            with st.spinner(f"Mengkonversi teks ke suara dengan suara '{selected_voice}'..."):
                speakable_text = format_recommendation_for_speech(st.session_state.recommendation_text)
                if "tidak dapat dibacakan" in speakable_text or "tidak sesuai" in speakable_text :
                    st.warning(speakable_text)
                else:
                    generate_and_play_speech(speakable_text, voice_choice=selected_voice)
        
        st.markdown("---") # Pemisah visual

        # Tombol Unduh PDF
        if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Unduh Rekomendasi sebagai PDF",
                    data=pdf_file,
                    file_name=os.path.basename(st.session_state.pdf_path), # Gunakan nama file dinamis dari save_as_pdf
                    mime="application/pdf",
                    key="btn_unduh_pdf"
                )
        elif st.session_state.pdf_path: # Path ada tapi file tidak ditemukan
            st.error("File PDF tidak ditemukan. Coba generate ulang rekomendasi.")

    if st.session_state.show_success_message:
        st.success("Terima kasih telah mengisi formulir! Rekomendasi Anda sudah siap.")
        st.session_state.show_success_message = False # Reset agar tidak muncul terus menerus

if __name__ == "__main__":
    main()
