import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import os

# 1. KONFIGURASI HALAMAN STREAMLIT (Elegant Dark Mode)
st.set_page_config(
    page_title="Samarinda Logistics Intelligence Dashboard",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi Gaya CSS untuk Tema Hitam-Emas Premium
st.markdown("""
    <style>
    .main { background-color: #13161c; color: #ffffff; }
    h1, h2, h3 { color: #d4af37 !important; }
    .stButton>button { background-color: #d4af37; color: #13161c; font-weight: bold; }
    .sidebar .sidebar-content { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

file_excel = "Dashboard_Ongkir_Samarinda_Lengkap.xlsx"
foto_profil = "poto_profil.jpeg"

# 2. FUNGSI UNTUK MEMBACA DAN TRANFORMASI DATA (Melt Matrix Kelurahan) - REVISI ANTI-MULTIINDEX
@st.cache_data
def load_and_transform_data():
    if not os.path.exists(file_excel):
        return None
    
    # Membaca data dari baris ke-3 (Header asli kelurahan)
    df_raw = pd.read_excel(file_excel, header=3)
    df_raw.columns = df_raw.columns.str.strip()
    
    # Ambil kolom pertama secara tegas sebagai ID Kurir/Ekspedisi (String Tunggal, bukan List)
    id_vars = str(df_raw.columns[0])
    
    # Mengambil semua kolom kelurahan (selain kolom pertama dan kolom total)
    list_kelurahan = [str(c) for c in df_raw.columns if c != id_vars and 'total' not in str(c).lower() and 'unnamed' not in str(c).lower()]
    
    # Melelehkan matriks (Melt) dengan ID tunggal yang aman
    df_long = pd.melt(
        df_raw, 
        id_vars=[id_vars], 
        value_vars=list_kelurahan, 
        var_name='Kelurahan', 
        value_name='Tarif'
    )
    
    # Pembersihan Data Tarif dari karakter non-angka
    df_long['Tarif'] = pd.to_numeric(df_long['Tarif'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    df_long = df_long.dropna(subset=['Tarif'])
    df_long = df_long.rename(columns={id_vars: 'Ekspedisi'})
    
    return df_long

df_clean = load_and_transform_data()

if df_clean is None:
    st.error(f"⚠️ Berkas '{file_excel}' tidak ditemukan di direktori saat ini. Pastikan file berada di folder yang sama dengan skrip ini.")
    st.stop()

# 3. SIDEBAR BRANDING PROFILE (Sesuai CV Anda)
with st.sidebar:
    if os.path.exists(foto_profil):
        st.image(foto_profil, width=120, caption="Rusnadi Aji Johansyah")
    st.markdown("### 🧑‍💻 Developer Profile")
    st.markdown("**Rusnadi Aji Johansyah**\n*Hukum Tata Negara Analyst & Developer Architect*")
    st.markdown("---")
    
    st.markdown("### ⚙️ Extraction Tech Stack")
    st.caption("• Python / BeautifulSoup\n• Chrome 9222 Hybrid Port (Bypass Bot)\n• Pandas Matrix Transformation")
    st.markdown("---")
    
    # Filter Interaktif untuk User
    st.markdown("### 🎛️ Filter Menu Dashboard")
    list_ekspedisi = sorted(df_clean['Ekspedisi'].unique())
    selected_ekspedisi = st.multiselect("Pilih Ekspedisi:", list_ekspedisi, default=list_ekspedisi[:3] if len(list_ekspedisi) >= 3 else list_ekspedisi)

# Filter data berdasarkan pilihan di sidebar
df_filtered = df_clean[df_clean['Ekspedisi'].isin(selected_ekspedisi)]

# 4. KONTEN UTAMA DASHBOARD
st.title("📍 Samarinda Regional Logistics Intelligence Dashboard")
st.markdown("Automated Legal Tech & Spasial Analisis Tarif Distribusi Logistik Kota Samarinda")
st.markdown("---")

# Ringkasan KPI Eksekutif (Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Data Ongkir Terdata", value=f"{len(df_filtered)} Rute")
with col2:
    if not df_filtered.empty and df_filtered['Tarif'].notna().any():
        mean_tarif = int(df_filtered['Tarif'].mean())
        st.metric(label="Rata-rata Tarif Logistik Kota", value=f"Rp {mean_tarif:,}")
    else:
        st.metric(label="Rata-rata Tarif Logistik Kota", value="Rp 0")
with col3:
    st.metric(label="Jumlah Ekspedisi Dipantau", value=f"{df_filtered['Ekspedisi'].nunique()} Provider")

st.markdown("---")

# Layout dua kolom untuk Grafik Interaktif
left_col, right_col = st.columns(2)

DARK_BG = "#13161c"       
GOLD_TEXT = "#d4af37"     
WHITE_TEXT = "#ffffff"    
GOLD_SCALE = ["#d4af37", "#f3e5ab", "#aa7c11", "#e6ca65"]

with left_col:
    st.subheader("📊 Efisiensi Tarif antar-Ekspedisi")
    if not df_filtered.empty:
        df_ekspedisi = df_filtered.groupby('Ekspedisi')['Tarif'].mean().reset_index().sort_values(by='Tarif')
        fig1 = px.bar(
            df_ekspedisi, x='Ekspedisi', y='Tarif', color='Ekspedisi',
            color_discrete_sequence=GOLD_SCALE, template='plotly_dark', text_auto='.2s'
        )
        fig1.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG, font=dict(color=WHITE_TEXT), showlegend=False)
        st.plotly_chart(fig1, width='stretch')
    else:
        st.info("Silakan pilih ekspedisi di sidebar.")

with right_col:
    st.subheader("📈 Top 10 Kelurahan dengan Tarif Tertinggi")
    if not df_filtered.empty:
        df_wilayah = df_filtered.groupby('Kelurahan')['Tarif'].mean().reset_index().sort_values(by='Tarif', ascending=False).head(10)
        fig2 = px.line(df_wilayah, x='Kelurahan', y='Tarif', markers=True, template='plotly_dark')
        fig2.update_traces(line=dict(color=GOLD_TEXT, width=4), marker=dict(size=10, color="#ffffff"))
        fig2.update_layout(plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG, font=dict(color=WHITE_TEXT))
        st.plotly_chart(fig2, width='stretch')
    else:
        st.info("Silakan pilih ekspedisi di sidebar.")

st.markdown("---")

# 5. INTEGRASI PETA INTERAKTIF (SPATIAL ANALYSIS)
st.subheader("🗺️ Pemetaan Spasial Wilayah Hukum & Logistik Samarinda")
st.markdown("Analisis visual jangkauan tarif berdasarkan titik koordinat pusat Kota Samarinda.")

# Titik pusat Samarinda
m = folium.Map(location=[-0.5021, 117.1536], zoom_start=12, tiles="CartoDB dark_matter")

# Mengambil kelurahan termahal untuk ditandai di peta secara interaktif
if not df_filtered.empty:
    df_map_data = df_filtered.groupby('Kelurahan')['Tarif'].mean().reset_index().sort_values(by='Tarif', ascending=False).head(10)
    for index, row in df_map_data.iterrows():
        folium.CircleMarker(
            location=[-0.5021 + (index*0.008 - 0.04), 117.1536 + (index*0.008 - 0.04)], 
            radius=8,
            popup=f"Kelurahan: {row['Kelurahan']}<br>Rata-rata Tarif: Rp {int(row['Tarif']):,}",
            color='#d4af37',
            fill=True,
            fill_color='#d4af37',
            fill_opacity=0.7
        ).add_to(m)

# Tampilkan Peta di Web Streamlit
st_folium(m, width="100%", height=500)

# 6. TABEL RAW DATA YANG BISA DI-FILTER USER
st.markdown("---")
st.subheader("🗂️ Data Ekstraksi Master Transparan")
st.dataframe(df_filtered, width='stretch')
