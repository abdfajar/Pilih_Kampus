import os
import openai
import streamlit as st
from fpdf import FPDF

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

def call_openai_api(prompt):
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Anda adalah asisten yang memberikan rekomendasi jurusan dan kampus."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        top_p=0.9
    )
    return response.choices[0].message.content

def save_as_pdf(profil, rekomendasi):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Hasil Rekomendasi Jurusan & Kampus", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Profil Pengguna:\n{profil}\n")
    pdf.ln(5)
    
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(0, 10, "Rekomendasi:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, rekomendasi)
    
    pdf_output = "rekomendasi_jurusan.pdf"
    pdf.output(pdf_output)
    return pdf_output

def main():
    st.title("📝 Formulir Pemilihan Jurusan & Kampus")
    st.write("Silakan isi formulir berikut untuk mengetahui rekomendasi jurusan dan kampus yang sesuai dengan minat dan potensi Anda.")

    # Informasi Pribadi
    st.header("📌 Informasi Pribadi")
    nama = st.text_input("Nama Lengkap")
    jenis_kelamin = st.radio("Jenis Kelamin", ("Laki-laki", "Perempuan"))
    usia = st.number_input("Usia", min_value=15, max_value=30, step=1)
    domisili = st.text_input("Kota/Kabupaten Domisili")
    sekolah = st.text_input("Sekolah Asal")
    jurusan_sma = st.selectbox("Jurusan SMA", ["IPA", "IPS", "Bahasa", "Lainnya"])
    nilai_rapor = st.slider("Nilai rata-rata rapor semester terakhir", min_value=0.0, max_value=100.0, step=0.1)

    # Profil Orang Tua atau Wali
    st.header("📌 Profil Orang Tua/Wali")
    nama_orangtua = st.text_input("Nama Orang Tua/Wali")
    hubungan = st.selectbox("Hubungan dengan Anda", ["Ayah", "Ibu", "Wali Lainnya"])
    pekerjaan = st.text_input("Pekerjaan Orang Tua/Wali")
    pendapatan = st.selectbox("Kisaran Pendapatan per Bulan", ["< Rp3 juta", "Rp3-5 juta", "Rp5-10 juta", "> Rp10 juta"])
    kontak_orangtua = st.text_input("Nomor Kontak Orang Tua/Wali")

    # Minat dan Preferensi Akademik
    st.header("📌 Minat dan Preferensi Akademik")
    mata_pelajaran = st.multiselect(
        "Mata pelajaran favorit", 
        ["Matematika", "Fisika", "Kimia", "Biologi", "Ekonomi", "Sosiologi", "Sejarah", "Bahasa Inggris", "Seni dan Desain", "Teknologi Informasi"]
    )
    aktivitas_suka = st.multiselect(
        "Aktivitas yang paling Anda sukai", 
        ["Menganalisis data", "Melakukan eksperimen", "Menciptakan karya seni", "Berkomunikasi", "Mengembangkan aplikasi", "Berwirausaha"]
    )
    gaya_belajar = st.radio("Gaya Belajar", ["Visual", "Auditori", "Kinestetik"])

    # Kepribadian dan Gaya Hidup
    st.header("📌 Kepribadian dan Gaya Hidup")
    lingkungan_kerja = st.selectbox("Saya lebih suka bekerja di", ["Kantor", "Lapangan", "Studio Kreatif"])
    karier = st.selectbox("Saya ingin berkarier di bidang", ["Teknologi", "Kesehatan", "Bisnis", "Sosial", "Seni"])
    kerja_tim = st.radio("Saya lebih suka bekerja secara", ["Mandiri", "Tim kecil", "Tim besar"])
    lingkungan_kampus = st.selectbox("Saya ingin kampus dengan lingkungan", ["Modern", "Tradisional", "Ramah mahasiswa"])

    # Prospek Karier dan Pengembangan Diri
    st.header("📌 Prospek Karier dan Pengembangan Diri")
    gaji_tinggi = st.slider("Seberapa penting potensi gaji yang tinggi?", 1, 5, 3)
    stabilitas_pekerjaan = st.slider("Seberapa penting stabilitas pekerjaan?", 1, 5, 3)
    kesempatan_luar_negeri = st.slider("Seberapa penting kesempatan kerja di luar negeri?", 1, 5, 3)
    fleksibilitas_karier = st.slider("Seberapa penting fleksibilitas karier?", 1, 5, 3)
    hobi_minat = st.slider("Seberapa penting jurusan sesuai dengan minat pribadi?", 1, 5, 3)

    # Preferensi Kampus
    st.header("📌 Rekomendasi Kampus")
    jenis_kampus = st.selectbox("Saya lebih tertarik dengan kampus", ["Negeri", "Swasta", "Spesialisasi Tertentu", "Internasional"])
    faktor_kampus = st.multiselect("Faktor utama dalam memilih kampus", ["Lokasi", "Akreditasi", "Biaya", "Fasilitas", "Beasiswa"])

    # Tombol Submit
    if st.button("Dapatkan Rekomendasi"): 

        profil_ringkas = (
            f"{nama}, seorang {jenis_kelamin} berusia {usia} tahun dari {domisili}, lulusan {sekolah} dengan jurusan {jurusan_sma} "
            f"dan nilai rata-rata {nilai_rapor}. Orang tua/wali, {nama_orangtua}, bekerja sebagai {pekerjaan} dengan pendapatan {pendapatan}. "
            f"Minat akademiknya meliputi {', '.join(mata_pelajaran)} dan lebih suka bekerja di {lingkungan_kerja}. "
            f"Mereka ingin berkarier di bidang {karier} dan lebih suka bekerja dalam {kerja_tim}. Kampus idealnya adalah {jenis_kampus} "
            f"dengan faktor utama {', '.join(faktor_kampus)}."
            f" dengan mempertimbangkan Prospek Karier dan Pengembangan Diri "
            f"- Potensi Gaji Tinggi: {gaji_tinggi}/5\n"
            f"- Stabilitas Pekerjaan: {stabilitas_pekerjaan}/5\n"
            f"- Kesempatan Kerja di Luar Negeri: {kesempatan_luar_negeri}/5\n"
            f"- Fleksibilitas Karier: {fleksibilitas_karier}/5\n"
            f"- Kesesuaian dengan Minat Pribadi: {hobi_minat}/5\n"
        )
        
                
        prompt = generate_prompt(profil_ringkas)
        response = call_openai_api(prompt)
        
        st.subheader("📌 Hasil Rekomendasi")
        st.markdown(f"### 📋 Ringkasan Profil Anda")
        st.markdown(profil_ringkas)
        st.markdown(f"### 🎓 Rekomendasi Jurusan & Kampus")
        st.markdown(response, unsafe_allow_html=True)

        ##st.markdown(f"### 🎓 Rekomendasi Jurusan & Kampus")
        ##st.markdown(f"```markdown\n{response}\n```")
        
        pdf_path = save_as_pdf(profil_ringkas, response)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Unduh Rekomendasi sebagai PDF",
                data=pdf_file,
                file_name="rekomendasi_jurusan.pdf",
                mime="application/pdf"
            )
        
        st.success("Terima kasih telah mengisi formulir! Gunakan informasi ini untuk menentukan pilihan terbaik Anda.")

if __name__ == "__main__":
    main()
