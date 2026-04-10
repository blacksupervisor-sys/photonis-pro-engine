import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Radar Gemini", layout="centered")

st.title("📡 Radar Gemini (Scanner)")
st.markdown("Mari kita bongkar model apa saja yang **sebenarnya** diizinkan oleh API Key Anda.")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ GEMINI_API_KEY tidak ditemukan di Streamlit Secrets.")
    st.stop()

if st.button("🚀 Pindai Server Google Sekarang"):
    with st.spinner("Membongkar brankas server Google..."):
        try:
            available_models = []
            # Mengambil semua model yang mendukung pembuatan konten
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if available_models:
                st.success("✅ Berhasil! Ini adalah daftar nama model yang SAH dan BISA Anda gunakan:")
                for model_name in available_models:
                    st.code(model_name)
                    
                st.info("💡 **SOLUSI:** Lihat daftar di atas. Cari yang ada tulisan 'flash' atau 'pro'. Copy nama tersebut persis seperti yang tertulis (misal: `models/gemini-1.5-flash`), lalu nanti kita tempelkan ke aplikasi utama kita.")
            else:
                st.error("❌ API Key Anda valid, tapi kosong! Tidak ada model yang diizinkan. Anda WAJIB membuat API Key baru murni dari aistudio.google.com.")
        except Exception as e:
            st.error(f"🚨 Terjadi kesalahan pemindaian: {e}")
