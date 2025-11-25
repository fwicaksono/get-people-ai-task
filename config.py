import os
import streamlit as st
import google.generativeai as genai
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Ambil ENV sesuai struktur terbaru
host = os.getenv("SUPA_HOST")
port = os.getenv("SUPA_PORT")
db_name = os.getenv("DBNAME")
user = os.getenv("SUPA_USER")
password = os.getenv("PASSWORD")

# Encode password
password_encoded = quote_plus(password)

# 3. Susun connection string
DB_URL = f"postgresql://{user}:{password_encoded}@{host}:{port}/{db_name}"

# 4. Validasi Config
if not DB_URL or not GEMINI_KEY:
    st.error("⚠️ Error: The .env file has an issue. Make sure SUPA_HOST, SUPA_USER, PASSWORD, and GEMINI_API_KEY are correct.")
    st.stop()

# 5. Setup Gemini
genai.configure(api_key=GEMINI_KEY)

# 6. Setup Database Engine (cached)
@st.cache_resource
def get_db_engine():
    try:
        engine = create_engine(DB_URL)
        # Test quick connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

# Jalankan koneksi
engine = get_db_engine()

if engine:
    st.success("✅ Database Connected Successfully!")
