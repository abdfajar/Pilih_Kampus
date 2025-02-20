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

    # Tombol Submit
    if st.button("Dapatkan Rekomendasi"): 
        profil_ringkas = (
            f"**Nama:** {nama}\n"
            f"**Jenis Kelamin:** {jenis_kelamin}\n"
            f"**Usia:** {usia}\n"
            f"**Domisili:** {domisili}\n"
            f"**Sekolah Asal:** {sekolah}\n"
            f"**Jurusan SMA:** {jurusan_sma}\n"
            f"**Nilai Rata-rata Rapor:** {nilai_rapor}\n"
        )
        
        prompt = generate_prompt(profil_ringkas)
        response = call_openai_api(prompt)
        
        st.subheader("📌 Hasil Rekomendasi")
        st.markdown(f"### 📋 Ringkasan Profil Anda")
        st.markdown(profil_ringkas)
        
        st.markdown(f"### 🎓 Rekomendasi Jurusan & Kampus")
        st.markdown(f"```markdown\n{response}\n```")
        
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
