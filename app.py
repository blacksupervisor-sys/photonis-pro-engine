import streamlit as st
import google.generativeai as genai
import requests
import io
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Mesin Fotonis Pro", page_icon="🚀", layout="wide")

# --- AMBIL API KEYS ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    REMOVE_BG_API_KEY = st.secrets["REMOVE_BG_API_KEY"]
    
    # Konfigurasi Library Resmi Google
    genai.configure(api_key=GEMINI_KEY)
except KeyError:
    st.error("⚠️ API Key belum lengkap di Streamlit Secrets.")
    st.stop()

st.title("🚀 Mesin Fotonis Pro: Ultralight")
st.markdown("**Sistem Pembuat Katalog & Analisa Ekspor Global (Generasi 2.0)**")

# --- FUNGSI HAPUS BACKGROUND VIA API ---
def remove_bg_api(image_bytes):
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': image_bytes},
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVE_BG_API_KEY},
    )
    if response.status_code == requests.codes.ok:
        return response.content
    else:
        st.error(f"Gagal hapus background: {response.text}")
        return None

# --- FUNGSI ANALISA GEMINI (MENGGUNAKAN MODEL 2.0) ---
def analisa_gemini_sdk(image_bytes):
    # Menggunakan model 2.0 yang SAH dari hasil radar Anda
    model = genai.GenerativeModel('gemini-pro-vision')
    
    img_pil = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    Anda adalah pakar pemasaran alat berat dan industrial global. 
    Analisa gambar produk ini dan berikan output berikut:
    1. **Nama Produk:** (Komersial & Profesional)
    2. **Spesifikasi Utama:** (Estimasi teknis berdasarkan visual)
    3. **Copywriting Sales Global:** (Gunakan metode AIDA dalam Bahasa Inggris untuk target pasar Ekspor)
    Format jawaban menggunakan Markdown yang rapi dan profesional.
    """
    
    response = model.generate_content([prompt, img_pil])
    return response.text

# --- UI UTAMA ---
uploaded_file = st.file_uploader("Upload Foto Produk", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = uploaded_file.read()
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(file_bytes, caption="Original", use_column_width="always")
    
    with col2:
        if st.button("✨ Proses Cepat"):
            with st.spinner("Memotong background dalam hitungan detik..."):
                result_bytes = remove_bg_api(file_bytes)
                if result_bytes:
                    st.session_state['gambar_bersih'] = result_bytes 
                    st.image(result_bytes, caption="Hasil Bersih", use_column_width="always")
                    st.success("Background berhasil dihapus!")

    st.divider()
    
    # --- TOMBOL AI GLOBAL ---
    if st.button("🌍 Analisa AI Global"):
        if 'gambar_bersih' not in st.session_state:
            st.warning("⚠️ Silakan klik 'Proses Cepat' terlebih dahulu.")
        else:
            with st.spinner("Gemini 2.0 sedang menyusun spesifikasi ekspor global..."):
                try:
                    hasil_ai = analisa_gemini_sdk(st.session_state['gambar_bersih'])
                    st.success("✅ Analisa Selesai!")
                    
                    with st.container(border=True):
                        st.markdown(hasil_ai)
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
