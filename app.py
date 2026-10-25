import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
import pandas as pd
from datetime import datetime
import base64
from PIL import Image
import io
import urllib.parse

st.set_page_config(page_title="Quilichao PropTech", page_icon="🏘️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8F9FA; }
    header {visibility: hidden;} footer {visibility: hidden;} #MainMenu {visibility: hidden;}
    .main-header { background: linear-gradient(135deg, #1E3A8A, #3B82F6); padding: 2rem; border-radius: 16px; color: white; text-align: center; margin-bottom: 20px; }
    .card { background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .prop-price { color: #059669; font-size: 1.2rem; font-weight: 800; }
    .badge-tipo { background: #E0E7FF; color: #1E3A8A; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "quilichao_proptech.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS predios (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, tipo TEXT, precio INTEGER, area REAL, habitaciones INTEGER, banos INTEGER, descripcion TEXT, lat REAL, lon REAL, direccion TEXT, barrio TEXT, comisionista TEXT, whatsapp TEXT, foto_base64 TEXT, fecha_registro TEXT)""")
    conn.commit(); conn.close()

def get_predios():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM predios ORDER BY fecha_registro DESC", conn)
    conn.close(); return df

def insert_predio(d):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""INSERT INTO predios (titulo, tipo, precio, area, habitaciones, banos, descripcion, lat, lon, direccion, barrio, comisionista, whatsapp, foto_base64, fecha_registro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d["titulo"], d["tipo"], d["precio"], d["area"], d["habitaciones"], d["banos"], d["descripcion"], d["lat"], d["lon"], d["direccion"], d["barrio"], d["comisionista"], d["whatsapp"], d["foto_base64"], datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

def cargar_ejemplos():
    # ¡Aquí están los 5 ejemplos restaurados!
    ejemplos = [
        ("Casa esquinera Barrio Centro", "Casa", 280_000_000, 120, 3, 2, "Casa esquinera en el corazón de Quilichao, cerca al parque principal.", 2.9963, -76.5922, "Calle 5 # 10-23", "Centro", "Carlos Muñoz", "3001234567"),
        ("Lote 500m² vía Mondomo", "Lote", 150_000_000, 500, 0, 0, "Lote plano con acceso a vía principal.", 3.0220, -76.5510, "Km 5 vía Mondomo", "Rural", "Carlos Muñoz", "3001234567"),
        ("Apartamento moderno Las Américas", "Apartamento", 195_000_000, 78, 2, 2, "Apartamento con acabados modernos, balcón y parqueadero.", 2.9925, -76.5850, "Carrera 8 # 12-45", "Las Américas", "Carlos Muñoz", "3001234567"),
        ("Finca recreativa San Antonio", "Finca", 450_000_000, 3000, 4, 3, "Finca con casa principal, piscina y cultivos.", 3.0450, -76.6100, "Corregimiento San Antonio", "Rural", "Carlos Muñoz", "3001234567"),
        ("Local comercial Parque Principal", "Local comercial", 320_000_000, 60, 0, 1, "Local sobre vía principal, alto flujo peatonal.", 2.9965, -76.5915, "Calle 4 # 9-12", "Centro", "Carlos Muñoz", "3001234567"),
    ]
    for e in ejemplos: 
        insert_predio({"titulo": e[0], "tipo": e[1], "precio": e[2], "area": e[3], "habitaciones": e[4], "banos": e[5], "descripcion": e[6], "lat": e[7], "lon": e[8], "direccion": e[9], "barrio": e[10], "comisionista": e[11], "whatsapp": e[12], "foto_base64": None})

def format_cop(precio): return "$" + f"{int(precio):,}".replace(",", ".")

init_db()

st.markdown('<div class="main-header"><h1>🏘️ Quilichao PropTech</h1><p>Gestión inteligente para comisionistas</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧭 Navegación")
    menu = st.radio("Ir a:", ["🏠 Inicio", "➕ Registrar", "🗺️ Mapa", "📋 Mis Predios"], label_visibility="collapsed")
    st.divider()
    if st.button("📥 Cargar datos de ejemplo"):
        cargar_ejemplos(); st.success("5 predios de ejemplo cargados"); st.rerun()

df = get_predios()

if menu == "🏠 Inicio":
    c1, c2 = st.columns(2)
    c1.metric("Predios en cartera", len(df))
    c2.metric("Valor total", format_cop(df["precio"].sum()) if len(df)>0 else "$0")
    st.markdown("### 🆕 Últimos predios")
    for _, row in df.head(3).iterrows():
        st.markdown(f'<div class="card"><span class="badge-tipo">{row["tipo"]}</span><h4>{row["titulo"]}</h4><p class="prop-price">{format_cop(row["precio"])}</p><p>📍 {row["direccion"]}</p></div>', unsafe_allow_html=True)

elif menu == "➕ Registrar":
    st.markdown("### ➕ Registrar Predio")
    if "pick_lat" not in st.session_state: st.session_state.pick_lat, st.session_state.pick_lon = 2.9963, -76.5922
    m_pick = folium.Map(location=[st.session_state.pick_lat, st.session_state.pick_lon], zoom_start=14)
    folium.Marker([st.session_state.pick_lat, st.session_state.pick_lon]).add_to(m_pick)
    map_result = st_folium(m_pick, height=300, width=None, returned_objects=["last_clicked"], key="picker")
    if map_result and map_result.get("last_clicked"):
        st.session_state.pick_lat = map_result["last_clicked"]["lat"]; st.session_state.pick_lon = map_result["last_clicked"]["lng"]; st.rerun()

    with st.form("form"):
        titulo = st.text_input("Título"); tipo = st.selectbox("Tipo", ["Casa", "Apartamento", "Lote", "Finca"]); precio = st.number_input("Precio", min_value=0); area = st.number_input("Área m²")
        direccion = st.text_input("Dirección"); barrio = st.text_input("Barrio"); comisionista = st.text_input("Nombre"); whatsapp = st.text_input("WhatsApp")
        if st.form_submit_button("Guardar"):
            insert_predio({"titulo": titulo, "tipo": tipo, "precio": precio, "area": area, "habitaciones": 0, "banos": 0, "descripcion": "", "lat": st.session_state.pick_lat, "lon": st.session_state.pick_lon, "direccion": direccion, "barrio": barrio, "comisionista": comisionista, "whatsapp": whatsapp, "foto_base64": None})
            st.success("Guardado"); st.rerun()

elif menu == "🗺️ Mapa":
    if len(df) > 0:
        m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=14)
        for _, row in df.iterrows(): folium.Marker([row["lat"], row["lon"]], popup=row["titulo"]).add_to(m)
        st_folium(m, width=None, height=500, returned_objects=[])

elif menu == "📋 Mis Predios":
    for _, row in df.iterrows():
        with st.expander(f"{row['titulo']} - {format_cop(row['precio'])}"):
            st.write(f"📍 {row['direccion']}")
            if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                conn = sqlite3.connect(DB_FILE); conn.execute("DELETE FROM predios WHERE id=?", (row["id"],)); conn.commit(); conn.close(); st.rerun()
