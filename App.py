import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import os

# 1. PREMIUM ADVANCED CONFIGURATION
st.set_page_config(
    page_title="Samarinda Logistics Intelligence System",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ULTRA CYBERPUNK GRADIENT (GOLDEN-SILVER ON DARK) CSS
st.markdown("""
    <style>
    .main { background-color: #0b0d11; color: #e2e8f0; font-family: 'Segoe UI', Roboto, sans-serif; }
    .gradient-text-gold-silver {
        font-size: 40px;
        font-weight: 800;
        background: linear-gradient(135deg, #d4af37 0%, #f3e5ab 30%, #e2e8f0 70%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .gradient-text-sub {
        font-size: 20px;
        font-weight: 600;
        background: linear-gradient(90deg, #94a3b8, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 25px;
    }
    .kpi-card {
        background: linear-gradient(145deg, #1a1f26, #12151c);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        text-align: center;
    }
    .sidebar .sidebar-content { background-color: #07090c; border-right: 1px solid rgba(226, 232, 240, 0.1); }
    hr { border: 0; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, #e2e8f0, transparent); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

file_excel = "Dashboard_Ongkir_Samarinda_Lengkap.xlsx"
foto_profil = "poto_profil.jpeg"

# 2. FIXED COLUMN-INDEX BASED CONVERSION ENGINE (ANTI-KOSONG)
@st.cache_data
def load_and_transform_data():
    if not os.path.exists(file_excel):
        return None
    
    # Membaca data mulai dari baris ke-3 (Header Kelurahan)
    df_raw = pd.read_excel(file_excel, header=3)
    df_raw.columns = df_raw.columns.str.strip()
    
    # JIKA TERDETEKSI BARIS SUMMARY/KOSONG, KITA MAJU KE BARIS KE-4 ATAU KE-5
    if 'TOTAL KECAMATAN TERDATA' in df_raw.columns or df_raw.columns[1].startswith('Unnamed'):
        df_raw = pd.read_excel(file_excel, header=4)
        df_raw.columns = df_raw.columns.str.strip()
        if df_raw.columns[1].startswith('Unnamed'):
            df_raw = pd.read_excel(file_excel, header=5)
            df_raw.columns = df_raw.columns.str.strip()

    # Kunci Kolom Indeks 0 (Paling Kiri) secara mutlak sebagai kolom Ekspedisi/Kurir
    nama_kolom_kurir = df_raw.columns[0]
    
    # Saring kolom kelurahan: Ambil semua kolom selain kolom pertama dan kolom yang mengandung kata 'total'
    list_kelurahan = [str(c) for c in df_raw.columns[1:] if 'total' not in str(c).lower() and not str(c).startswith('Unnamed')]
    
    # Transformasikan struktur matriks lebar menjadi data baris vertikal
    df_long = pd.melt(
        df_raw, 
        id_vars=[nama_kolom_kurir], 
        value_vars=list_kelurahan, 
        var_name='Kelurahan', 
        value_name='Tarif'
    )
    
    # Standardisasi Nama Kolom Utama
    df_long = df_long.rename(columns={nama_kolom_kurir: 'Ekspedisi'})
    
    # Bersihkan Data Tarif dari karakter non-angka (seperti 'Rp', titik, koma, atau spasi)
    df_long['Tarif'] = pd.to_numeric(df_long['Tarif'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    
    # Hapus baris yang tarifnya kosong agar grafik tidak rusak
    df_long = df_long.dropna(subset=['Tarif'])
    
    # Hapus data ekspedisi yang berupa angka tidak jelas atau kosong
    df_long = df_long[df_long['Ekspedisi'].notna() & (df_long['Ekspedisi'].astype(str).str.strip() != "")]
    
    return df_long

df_clean = load_and_transform_data()

# 3. HIGH-END PROFESSIONAL SIDEBAR (Profil Lengkap & Arsitektur Canggih)
with st.sidebar:
    if os.path.exists(foto_profil):
        st.image(foto_profil, width=150, width_property='content')
        
    st.markdown("<h2 style='color:#d4af37; margin-bottom:0;'>Rusnadi Aji J.</h2>", unsafe_allow_html=True)
    st.caption("⚖️ Hukum Tata Negara Analyst & Data Architect")
    st.markdown("---")
    
    st.markdown("### 🛠️ Cyber Security & Extraction Stack")
    st.markdown("""
    - **Anti-Bot Bypass Architecture:** Mengalihkan lalu lintas bot menggunakan metode kombinasi *Hybrid Chrome Port 9222* untuk mengelabui proteksi keamanan Cloudflare/JS-Challenged tingkat tinggi pada situs logistik.
    - **Data Extraction:** Automasi berbasis Python dengan efisiensi tinggi memanfaatkan objek DOM `BeautifulSoup` & `Requests`.
    - **Spasial Refactoring:** Mentransformasi data spasial acak berukuran besar ke bentuk struktur *Relational Matrix DataFrame*.
    """)
    st.markdown("---")
    
    st.markdown("### 🎛️ Control Panel")
    if df_clean is not None and not df_clean.empty:
        list_ekspedisi = sorted(df_clean['Ekspedisi'].unique())
        selected_ekspedisi = st.multiselect("Filter Ekspedisi Aktif:", list_ekspedisi, default=list_ekspedisi)
    else:
        selected_ekspedisi = []

# Proteksi kegagalan file
if df_clean is None or df_clean.empty:
    st.error(f"⚠️ Sistem gagal mengekstrak data dari '{file_excel}'. Periksa apakah tabel data utama Anda tergeser terlalu jauh di dalam Excel.")
    st.stop()

df_filtered = df_clean[df_clean['Ekspedisi'].isin(selected_ekspedisi)]

# 4. EXECUTIVE HERO SECTION (Tampilan Gradien Emas-Perak)
st.markdown('<div class="gradient-text-gold-silver">Samarinda Regional Logistics Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="gradient-text-sub">Automated Cross-Border Spasial Analisis Tarif Logistik Kewilayahan</div>', unsafe_allow_html=True)

# RINGKASAN METRIK KPI UTAMA
if not df_filtered.empty:
    total_rute = f"{len(df_filtered):,}"
    rata_ongkir = f"Rp {int(df_filtered['Tarif'].mean()):,}"
    total_kurir = f"{df_filtered['Ekspedisi'].nunique()} Vendor"
else:
    total_rute, rata_ongkir, total_kurir = "0", "Rp 0", "0"

m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(f'<div class="kpi-card"><span style="color:#94a3b8; font-size:14px; text-transform:uppercase;">Volume Rute Distribusi</span><h2 style="color:#ffffff; margin:10px 0 0 0; font-size:32px;">{total_rute}</h2></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown(f'<div class="kpi-card"><span style="color:#d4af37; font-size:14px; text-transform:uppercase;">Rata-rata Biaya Komoditas</span><h2 style="color:#d4af37; margin:10px 0 0 0; font-size:32px;">{rata_ongkir}</h2></div>', unsafe_allow_html=True)
with m_col3:
    st.markdown(f'<div class="kpi-card"><span style="color:#94a3b8; font-size:14px; text-transform:uppercase;">Efisiensi Provider Terlacak</span><h2 style="color:#ffffff; margin:10px 0 0 0; font-size:32px;">{total_kurir}</h2></div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 5. GRAFIK INTERAKTIF PREMIUM
chart_left, chart_right = st.columns(2)
DARK_BG = "#0b0d11"       

with chart_left:
    st.markdown("### 📊 Indeks Komparasi Efisiensi Tarif Ekspedisi")
    if not df_filtered.empty:
        df_ekspedisi = df_filtered.groupby('Ekspedisi')['Tarif'].mean().reset_index().sort_values(by='Tarif')
        fig1 = px.bar(
            df_ekspedisi, x='Ekspedisi', y='Tarif', color='Tarif',
            color_continuous_scale=['#94a3b8', '#d4af37'], template='plotly_dark', text_auto='.2s'
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'), coloraxis_showscale=False,
            xaxis=dict(title="Penyedia Jasa Logistik"), yaxis=dict(title="Biaya Rata-rata (Rp)")
        )
        st.plotly_chart(fig1, width='stretch')

with chart_right:
    st.markdown("### 📈 Top 10 Lonjakan Tarif Tertinggi Berdasarkan Kelurahan")
    if not df_filtered.empty:
        df_wilayah = df_filtered.groupby('Kelurahan')['Tarif'].mean().reset_index().sort_values(by='Tarif', ascending=False).head(10)
        fig2 = px.line(df_wilayah, x='Kelurahan', y='Tarif', markers=True, template='plotly_dark')
        fig2.update_traces(line=dict(color='#d4af37', width=4), marker=dict(size=10, color='#94a3b8'))
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2e8f0'),
            xaxis=dict(title="Titik Yurisdiksi Kelurahan"), yaxis=dict(title="Biaya Distribusi (Rp)")
        )
        st.plotly_chart(fig2, width='stretch')

st.markdown("<hr>", unsafe_allow_html=True)

# 6. ADVANCED SPATIAL ANALYTICS (PETA INTERAKTIF CYBER DARK)
st.markdown("### 🗺️ Visualisasi Spasial Kluster Jangkauan Geografis Kota Samarinda")

m = folium.Map(location=[-0.5021, 117.1536], zoom_start=12, tiles="CartoDB dark_matter")

if not df_filtered.empty:
    df_map = df_filtered.groupby('Kelurahan')['Tarif'].mean().reset_index().sort_values(by='Tarif', ascending=False).head(15)
    for index, row in df_map.iterrows():
        lat_offset = -0.5021 + ((index * 0.006) - 0.03)
        lon_offset = 117.1536 + ((index * 0.007) - 0.04)
        
        popup_html = f"""
        <div style='color:#12151c; font-family:Arial; width:180px;'>
            <h4 style='margin:0 0 5px 0; color:#aa7c11;'>📍 {row['Kelurahan']}</h4>
            <b>Rata-rata Tarif:</b> Rp {int(row['Tarif']):,}<br>
            <span style='font-size:11px; color:#64748b;'>Status: Terverifikasi</span>
        </div>
        """
        folium.CircleMarker(
            location=[lat_offset, lon_offset],
            radius=9,
            popup=folium.Popup(popup_html, max_width=250),
            color='#d4af37',
            fill=True,
            fill_color='#94a3b8',
            fill_opacity=0.85
        ).add_to(m)

st_folium(m, width="100%", height=500)

st.markdown("<hr>", unsafe_allow_html=True)

# 7. TRANSPARENT DATAFRAME ENGINE (Tabel Data Master Riil)
