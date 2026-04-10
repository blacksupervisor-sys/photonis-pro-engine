import streamlit as st
import google.generativeai as genai
import requests
import io
import datetime
from PIL import Image
from fpdf import FPDF

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Mesin Fotonis Pro - Visual Edition", page_icon="🏗️", layout="wide")

# --- AMBIL API KEYS ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    REMOVE_BG_API_KEY = st.secrets["REMOVE_BG_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except KeyError:
    st.error("⚠️ API Key belum lengkap di Streamlit Secrets.")
    st.stop()

# --- FUNGSI PDF DENGAN PRODUK & LOGO ---
class VISUAL_PDF(FPDF):
    def __init__(self, logo_image=None, brand_name="", product_image=None):
        super().__init__()
        self.logo_image = logo_image
        self.brand_name = brand_name
        self.product_image = product_image

    def header(self):
        # 1. Header Logo
        if self.logo_image:
            img_buf = io.BytesIO()
            self.logo_image.save(img_buf, format='PNG')
            img_buf.seek(0)
            self.image(img_buf, 10, 8, 30)
            self.set_x(45)
        
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, self.brand_name, border=False, ln=True, align='L')
        self.set_font('helvetica', 'I', 8)
        self.set_x(45) if self.logo_image else None
        self.cell(0, 5, f"Verified Technical Report | {datetime.date.today()}", ln=True)
        self.line(10, 40, 200, 40)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f"Developed by Adjie Agung - Mesin Fotonis Pro v3", align='C')

def create_visual_pdf(text, logo, brand, product_bytes):
    pdf = VISUAL_PDF(logo_image=logo, brand_name=brand)
    pdf.add_page()
    
    # 2. Masukkan Gambar Produk di Bagian Atas
    if product_bytes:
        prod_img = Image.open(io.BytesIO(product_bytes))
        prod_buf = io.BytesIO()
        prod_img.save(prod_buf, format='PNG')
        prod_buf.seek(0)
        # Menempatkan gambar produk di tengah
        pdf.image(prod_buf, x=55, y=45, w=100)
        pdf.ln(70) # Memberi ruang agar teks tidak menabrak gambar

    # 3. Masukkan Teks Analisa
    pdf.set_font("helvetica", size=10)
    normalized_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, normalized_text)
    
    return pdf.output()

# --- SIDEBAR: COMMAND CENTER ---
with st.sidebar:
    st.header("🎮 Command Center")
    user_brand = st.text_input("Nama Perusahaan/Brand", "TATSUO & AIMIX")
    user_logo = st.file_uploader("Upload Logo Brand (PNG)", type=['png', 'jpg'])
    
    st.divider()
    if st.button("🗑️ Reset Sesi"):
        st.session_state.clear()
        st.rerun()

# --- UI UTAMA ---
st.title("🏗️ Mesin Fotonis Pro: Visual Edition")
st.caption("Developed by **Adjie Agung** | Industrial AI Expert")

uploaded_file = st.file_uploader("📷 Upload Foto Unit", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = uploaded_file.read()
    col_img, col_ai = st.columns([1, 1])
    
    with col_img:
        st.image(file_bytes, caption="Original Asset", use_column_width="always")
        if st.button("✨ Hapus Background"):
            with st.spinner("Processing visual..."):
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
            st.image(st.session_state['clean_img'], caption="Asset Siap Katalog", use_column_width="always")
            if st.button("🧠 Jalankan Analisa AI"):
                with st.spinner("AI Menganalisa..."):
                    model = genai.GenerativeModel('gemini-flash-latest')
                    img_pil = Image.open(io.BytesIO(st.session_state['clean_img']))
                    res = model.generate_content(["Berikan spesifikasi teknis mendalam dan copywriting marketing AIDA untuk unit ini.", img_pil])
                    st.session_state['draft_text'] = res.text

    if 'draft_text' in st.session_state:
        st.divider()
        st.subheader("📝 Verifikasi Spesifikasi & Copywriting")
        # Field Editor agar Adjie bisa menyesuaikan spek nyata
        final_text = st.text_area("Edit teks di bawah ini agar sesuai dengan brosur asli:", value=st.session_state['draft_text'], height=350)
        
        c1, c2 = st.columns(2)
        with c1:
            logo_img = Image.open(user_logo) if user_logo else None
            # Membuat PDF dengan menyertakan GAMBAR PRODUK
            pdf_data = create_visual_pdf(final_text, logo_img, user_brand, st.session_state.get('clean_img'))
            
            st.download_button(
                label="📥 Download Katalog PDF (Visual)",
                data=bytes(pdf_data),
                file_name=f"Katalog_{user_brand}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with c2:
            wa_text = f"Berikut spek unit {user_brand}:\n\n{final_text[:400]}..."
            st.link_button("📲 Kirim via WhatsApp", f"https://wa.me/?text={requests.utils.quote(wa_text)}", use_container_width=True)
