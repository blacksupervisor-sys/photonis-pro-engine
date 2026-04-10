import streamlit as st
import google.generativeai as genai
import requests
import io
import datetime
from PIL import Image
from fpdf import FPDF

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Mesin Fotonis Pro - Custom Edition", page_icon="🏗️", layout="wide")

# --- AMBIL API KEYS ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    REMOVE_BG_API_KEY = st.secrets["REMOVE_BG_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except KeyError:
    st.error("⚠️ API Key belum lengkap di Streamlit Secrets.")
    st.stop()

# --- FUNGSI PDF CUSTOMIZABLE ---
class CUSTOM_PDF(FPDF):
    def __init__(self, logo_image=None, brand_name=""):
        super().__init__()
        self.logo_image = logo_image
        self.brand_name = brand_name

    def header(self):
        if self.logo_image:
            # Menyimpan logo ke buffer untuk dimasukkan ke PDF
            img_buf = io.BytesIO()
            self.logo_image.save(img_buf, format='PNG')
            img_buf.seek(0)
            self.image(img_buf, 10, 8, 33)
            self.set_x(45)
        
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, self.brand_name, border=False, ln=True, align='L')
        self.set_font('helvetica', 'I', 8)
        self.set_x(45) if self.logo_image else None
        self.cell(0, 5, f"Verified Technical Report - {datetime.date.today()}", ln=True)
        self.line(10, 45, 200, 45)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Developed by Adjie Agung", align='C')

def create_custom_pdf(text, logo, brand):
    pdf = CUSTOM_PDF(logo_image=logo, brand_name=brand)
    pdf.add_page()
    pdf.set_font("helvetica", size=10)
    
    normalized_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, normalized_text)
    
    return pdf.output()

# --- SIDEBAR: COMMAND CENTER ---
with st.sidebar:
    st.header("🎮 Command Center")
    user_brand = st.text_input("Nama Perusahaan/Brand", "TATSUO & AIMIX")
    user_logo = st.file_uploader("Upload Logo Laporan (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    st.subheader("🛠️ Koreksi Spek Teknis")
    st.info("AI akan memberikan draf, Anda bisa mengeditnya di area utama sebelum download.")
    
    if st.button("🗑️ Reset Semua Sesi"):
        st.session_state.clear()
        st.rerun()

# --- UI UTAMA ---
st.title("🏗️ Mesin Fotonis Pro: Custom Edition")

uploaded_file = st.file_uploader("📷 Upload Foto Unit", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = uploaded_file.read()
    col_img, col_ai = st.columns([1, 1])
    
    with col_img:
        st.image(file_bytes, caption="Original Asset", use_column_width="always")
        if st.button("✨ Hapus Background"):
            with st.spinner("Cleaning..."):
                response = requests.post(
                    'https://api.remove.bg/v1.0/removebg',
                    files={'image_file': file_bytes},
                    data={'size': 'auto'},
                    headers={'X-Api-Key': REMOVE_BG_API_KEY},
                )
                if response.status_code == requests.codes.ok:
                    st.session_state['clean_img'] = response.content
                    st.rerun()

    with col_ai:
        if 'clean_img' in st.session_state:
            st.image(st.session_state['clean_img'], caption="Asset Bersih", use_column_width="always")
            
            if st.button("🧠 Jalankan Analisa AI"):
                with st.spinner("AI Menganalisa Visual..."):
                    model = genai.GenerativeModel('gemini-flash-latest')
                    img_pil = Image.open(io.BytesIO(st.session_state['clean_img']))
                    res = model.generate_content(["Analisa detail alat berat ini dalam format poin-poin spesifikasi teknis dan copywriting AIDA.", img_pil])
                    st.session_state['draft_text'] = res.text

    if 'draft_text' in st.session_state:
        st.divider()
        st.subheader("📝 Review & Edit Hasil (Verifikasi Manusia)")
        st.warning("Silakan edit teks di bawah ini agar sesuai dengan spesifikasi nyata produk Anda.")
        
        # AREA EDITING MANUFAKTUR
        final_text = st.text_area("Hasil Analisa (Bisa Diedit)", value=st.session_state['draft_text'], height=400)
        
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            # Tombol Download PDF
            logo_to_use = Image.open(user_logo) if user_logo else None
            pdf_bytes = bytes(create_custom_pdf(final_text, logo_to_use, user_brand))
            st.download_button(
                label="📥 Download Laporan Terverifikasi (PDF)",
                data=pdf_bytes,
                file_name=f"Technical_Report_{user_brand}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with c2:
            # WhatsApp Direct
            wa_url = f"https://wa.me/?text={requests.utils.quote(final_text[:500])}"
            st.link_button("📲 Kirim Spek ke WhatsApp", wa_url, use_container_width=True)

st.markdown(f"--- \n <center><small>Developed by **Adjie Agung** | Enterprise Asset Intel</small></center>", unsafe_allow_html=True)
