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

# 1. Configuración Mobile-First
st.set_page_config(
    page_title="Quilichao PropTech",
    page_icon="🏘️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. CSS de App (Colores originales, layout móvil)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #F8F9FA; }
    .block-container { padding-top: 1.5rem; padding-bottom: 6rem; max-width: 600px; }
    
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #FFC300 0%, #FF5733 50%, #C70039 100%);
        padding: 1.5rem 1rem; border-radius: 20px; color: white;
        text-align: center; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(199, 0, 57, 0.2);
    }
    .main-header h1 { margin: 0; font-size: 24px; font-weight: 800; }
    .main-header p { margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; }

    .stat-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; padding: 15px; border-radius: 16px;
        text-align: center; box-shadow: 0 4px 10px rgba(30, 60, 114, 0.15);
    }
    .stat-box h3 { margin: 0; font-size: 20px; font-weight: 800; }
    .stat-box p { margin: 2px 0 0 0; font-size: 11px; opacity: 0.9; }

    .card {
        background: white; border-radius: 16px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; margin-bottom: 15px;
    }
    .prop-price { color: #C70039; font-size: 18px; font-weight: 800; }
    .badge-tipo { background: #FFC300; color: #1a1a1a; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }

    /* Botones navegación */
    div.stButton > button {
        background-color: white; color: #555; border: 1px solid #DDD;
        border-radius: 15px; padding: 8px 5px; width: 100%; font-weight: 600; font-size: 13px;
    }
    div.stButton > button[kind="primary"] { 
        background-color: #C70039; color: white; border: none; box-shadow: 0 4px 10px rgba(199, 0, 57, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 3. Lógica de Base de Datos
DB_FILE = "quilichao_proptech.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS predios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, tipo TEXT NOT NULL,
            precio INTEGER NOT NULL, area REAL NOT NULL, habitaciones INTEGER DEFAULT 0, banos INTEGER DEFAULT 0,
            descripcion TEXT, lat REAL NOT NULL, lon REAL NOT NULL, direccion TEXT NOT NULL, barrio TEXT,
            comisionista TEXT NOT NULL, whatsapp TEXT NOT NULL, foto_base64 TEXT, fecha_registro TEXT NOT NULL
        )
    """)
    conn.commit(); conn.close()

def get_predios():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM predios ORDER BY fecha_registro DESC", conn)
    conn.close(); return df

def insert_predio(d: dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO predios (titulo, tipo, precio, area, habitaciones, banos, descripcion, lat, lon, direccion, barrio, comisionista, whatsapp, foto_base64, fecha_registro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d["titulo"], d["tipo"], d["precio"], d["area"], d["habitaciones"], d["banos"], d["descripcion"], d["lat"], d["lon"], d["direccion"], d["barrio"], d["comisionista"], d["whatsapp"], d["foto_base64"], datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

def delete_predio(predio_id: int):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM predios WHERE id = ?", (predio_id,))
    conn.commit(); conn.close()

def format_cop(precio) -> str:
    try: return "$" + f"{int(precio):,}".replace(",", ".")
    except: return "$0"

def cargar_ejemplos():
    ejemplos = [("Casa Centro", "Casa", 280_000_000, 120, 3, 2, "Esquinera.", 2.9963, -76.5922, "Calle 5", "Centro", "Carlos", "3001234567")]
    for e in ejemplos:
        insert_predio({"titulo": e[0], "tipo": e[1], "precio": e[2], "area": e[3], "habitaciones": e[4], "banos": e[5], "descripcion": e[6], "lat": e[7], "lon": e[8], "direccion": e[9], "barrio": e[10], "comisionista": e[11], "whatsapp": e[12], "foto_base64": None})

init_db()

# 4. Estado de Navegación
if "pagina" not in st.session_state: st.session_state.pagina = "inicio"

# 5. Vistas
st.markdown("""
<div class="main-header">
    <h1>🏘️ Quilichao PropTech</h1>
    <p>Gestión para comisionistas</p>
</div>
""", unsafe_allow_html=True)

df = get_predios()

if st.session_state.pagina == "inicio":
    st.markdown("### Tu cartera")
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat-box"><h3>{len(df)}</h3><p>Predios</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-box"><h3>{format_cop(df["precio"].sum()/1_000_000) if len(df)>0 else "$0"}M</h3><p>Valor</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>### Últimos predios", unsafe_allow_html=True)
    if len(df) == 0: st.info("No hay predios. Ve a 'Registrar' o carga ejemplos.")
    for _, row in df.head(3).iterrows():
        st.markdown(f"""
        <div class="card">
            <span class="badge-tipo">{row['tipo']}</span>
            <h4 style="margin: 5px 0;">{row['titulo']}</h4>
            <p class="prop-price">{format_cop(row['precio'])}</p>
            <p style="font-size: 12px; color: #666;">📍 {row['direccion']}</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.pagina == "registrar":
    st.markdown("### ➕ Registrar Predio")
    if "pick_lat" not in st.session_state:
        st.session_state.pick_lat, st.session_state.pick_lon = 2.9963, -76.5922
        
    m_pick = folium.Map(location=[st.session_state.pick_lat, st.session_state.pick_lon], zoom_start=14)
    folium.Marker([st.session_state.pick_lat, st.session_state.pick_lon], icon=folium.Icon(color="red")).add_to(m_pick)
    map_result = st_folium(m_pick, height=250, width=None, returned_objects=["last_clicked"], key="picker")
    if map_result and map_result.get("last_clicked"):
        st.session_state.pick_lat = map_result["last_clicked"]["lat"]
        st.session_state.pick_lon = map_result["last_clicked"]["lng"]
        st.rerun()

    with st.form("form"):
        titulo = st.text_input("Título")
        tipo = st.selectbox("Tipo", ["Casa", "Apartamento", "Lote", "Finca", "Local"])
        precio = st.number_input("Precio (COP)", min_value=0, step=1000000)
        area = st.number_input("Área (m²)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            if titulo:
                insert_predio({"titulo": titulo, "tipo": tipo, "precio": precio, "area": area, "habitaciones": 0, "banos": 0, "descripcion": "", "lat": st.session_state.pick_lat, "lon": st.session_state.pick_lon, "direccion": "Ubicación Mapa", "barrio": "", "comisionista": "Yo", "whatsapp": "123", "foto_base64": None})
                st.success("Guardado"); st.rerun()

elif st.session_state.pagina == "mapa":
    st.markdown("### 🗺️ Mapa")
    if len(df) > 0:
        m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=14)
        for _, row in df.iterrows():
            folium.Marker([row["lat"], row["lon"]], popup=row['titulo']).add_to(m)
        st_folium(m, width=None, height=450, returned_objects=[])
    else: st.info("No hay predios en el mapa.")

elif st.session_state.pagina == "predios":
    st.markdown("### 📋 Mis Predios")
    if len(df) == 0: st.info("Cartera vacía.")
    for _, row in df.iterrows():
        with st.expander(f"{row['titulo']} - {format_cop(row['precio'])}"):
            st.write(f"📍 {row['direccion']} | {row['tipo']}")
            if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                delete_predio(int(row["id"])); st.rerun()

# 6. Barra de Navegación
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏠 Inicio", use_container_width=True, type="primary" if st.session_state.pagina=="inicio" else "secondary"):
        st.session_state.pagina = "inicio"; st.rerun()
with c2:
    if st.button("➕ Nuevo", use_container_width=True, type="primary" if st.session_state.pagina=="registrar" else "secondary"):
        st.session_state.pagina = "registrar"; st.rerun()
with c3:
    if st.button("🗺️ Mapa", use_container_width=True, type="primary" if st.session_state.pagina=="mapa" else "secondary"):
        st.session_state.pagina = "mapa"; st.rerun()
with c4:
    if st.button("📋 Lista", use_container_width=True, type="primary" if st.session_state.pagina=="predios" else "secondary"):
        st.session_state.pagina = "predios"; st.rerun()
