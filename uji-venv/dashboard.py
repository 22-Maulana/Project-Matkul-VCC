import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title="AI Vector Simulator", page_icon="🧠", layout="wide")
st.title("🧠 Visualisasi Matriks Vektor AI & Penguras RAM")
st.markdown("Dashboard interaktif ini tidak hanya menguras memori EC2 Anda, tetapi juga menyimulasikan antarmuka ekstraksi fitur berdimensi tinggi.")
@st.cache_data
def generate_vectors():
    return pd.DataFrame(np.random.randn(100000, 8), columns=[f"Dimensi {i}" for i in range(1, 9)])
with st.spinner("Memuat 100.000 vektor fitur ke dalam memori..."): 
    df = generate_vectors()
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Total Vektor Laten", "100,000 Baris", "Siap untuk Vector DB")
col2.metric("Konsumsi RAM Pandas", "Sangat Tinggi", "Stress Test Aktif", delta_color="inverse")
col3.metric("Status Komputasi", "Hybrid Search", "Optimal")
st.divider()
st.subheader("📊 Fluktuasi Vektor Laten (Dimensi 1 - 3)")
st.area_chart(df.iloc[:250, :3])
st.subheader("🗄️ Sampel Matriks Mentah")
st.dataframe(df.head(20), use_container_width=True)
