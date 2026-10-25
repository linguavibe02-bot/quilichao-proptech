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

# 2. CSS de App Profesional
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #F8F9FA; }
    .block-container { padding-top: 1.5rem; padding-bottom: 6rem; max-width: 600px; }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Encabezado Azul Profundo */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        padding: 1.5rem 1rem; border-radius: 20px; color: white;
        text-align: center; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(30, 58, 138, 0.2);
    }
    .main-header h1 { margin: 0; font-size: 24px; font-weight: 700; }
    .main-header p { margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; }

    /* Tarjetas */
    .card {
        background: white; border-radius: 16px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; margin-bottom: 15px;
    }
    .prop-price { color: #059669; font-size: 20px; font-weight: 700; }
    .badge-tipo { background: #E0E7FF; color: #1E3A8A; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .card-title { margin: 8px 0 4px 0; font-size: 16px; font-weight: 600; color: #1F2937; }
    .card-loc { font-size: 13px; color: #6B7280; }

    /* Botones de Navegación */
    div.stButton > button {
        background-color: white; color: #4B5563; border: 1px solid #E5E7EB;
        border-radius: 12px; padding: 8px 2px; width: 100%; font-weight: 600; font-size: 12px;
        transition: all 0.2s;
    }
    div.stButton > button[kind="primary"] { 
        background-color: #1E3A8A; color: white; border: none; box-shadow: 0 4px 10px rgba(30, 58, 138, 0.3);
    }
    
    /* Formularios */
    div[data-testid="stForm"] { background: white; border-radius: 16px; padding: 15px; border: 1px solid #EAEAEA; }
</style>
""", unsafe_allow_html=True)

# 3. Base de Datos
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
    ejemplos = [
        ("Casa esquinera Barrio Centro", "Casa", 280_000_000, 120, 3, 2, "Casa esquinera en el corazón de Quilichao, cerca al parque principal.", 2.9963, -76.5922, "Calle 5 # 10-23", "Centro", "Carlos Muñoz", "3001234567"),
        ("Lote 500m² vía Mondomo", "Lote", 150_000_000, 500, 0, 0, "Lote plano con acceso a vía principal.", 3.0220, -76.5510, "Km 5 vía Mondomo", "Rural", "Carlos Muñoz", "3001234567"),
        ("Apartamento moderno Las Américas", "Apartamento", 195_000_000, 78, 2, 2, "Apartamento con acabados modernos, balcón y parqueadero.", 2.9925, -76.5850, "Carrera 8 # 12-45", "Las Américas", "Carlos Muñoz", "3001234567"),
        ("Finca recreativa San Antonio", "Finca", 450_000_000, 3000, 4, 3, "Finca con casa principal, piscina y cultivos.", 3.0450, -76.6100, "Corregimiento San Antonio", "Rural", "Carlos Muñoz", "3001234567"),
        ("Local comercial Parque Principal", "Local comercial", 320_000_000, 60, 0, 1, "Local sobre vía principal, alto flujo peatonal.", 2.9965, -76.5915, "Calle 4 # 9-12", "Centro", "Carlos Muñoz", "3001234567"),
    ]
    for e in ejemplos:
        insert_predio({"titulo": e[0], "tipo": e[1], "precio": e[2], "area": e[3], "habitaciones": e[4], "banos": e[5], "descripcion": e[6], "lat": e[7], "lon": e[8], "direccion": e[9], "barrio": e[10], "comisionista": e[11], "whatsapp": e[12], "foto_base64": None})

init_db()

# 4. Control de Navegación
if "pagina" not in st.session_state: st.session_state.pagina = "inicio"

# 5. Renderizado de Páginas
st.markdown("""
<div class="main-header">
    <h1>🏘️ Quilichao PropTech</h1>
    <p>Gestión inteligente para comisionistas</p>
</div>
""", unsafe_allow_html=True)

df = get_predios()

if st.session_state.pagina == "inicio":
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="card" style="text-align:center;"><h3 style="color:#1E3A8A; margin:0;">{len(df)}</h3><p style="color:#6B7280; font-size:12px; margin:0;">Predios en cartera</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card" style="text-align:center;"><h3 style="color:#059669; margin:0;">{format_cop(df["precio"].sum()/1_000_000) if len(df)>0 else "$0"}M</h3><p style="color:#6B7280; font-size:12px; margin:0;">Valor total</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 🆕 Últimos predios")
    if len(df) == 0:
        st.info("Aún no tienes predios registrados.")
        if st.button("📥 Cargar 5 predios de ejemplo para probar"):
            cargar_ejemplos()
            st.rerun()
    else:
        for _, row in df.head(3).iterrows():
            st.markdown(f"""
            <div class="card">
                <span class="badge-tipo">{row['tipo']}</span>
                <h4 class="card-title">{row['titulo']}</h4>
                <p class="prop-price">{format_cop(row['precio'])}</p>
                <p class="card-loc">📍 {row['direccion']}, {row['barrio']}</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.pagina == "registrar":
    st.markdown("### ➕ Registrar Predio")
    if "pick_lat" not in st.session_state:
        st.session_state.pick_lat, st.session_state.pick_lon = 2.9963, -76.5922
        
    st.markdown("**📍 Toca el mapa para ubicar el predio**")
    m_pick = folium.Map(location=[st.session_state.pick_lat, st.session_state.pick_lon], zoom_start=14)
    folium.Marker([st.session_state.pick_lat, st.session_state.pick_lon], icon=folium.Icon(color="red")).add_to(m_pick)
    map_result = st_folium(m_pick, height=250, width=None, returned_objects=["last_clicked"], key="picker")
    if map_result and map_result.get("last_clicked"):
        st.session_state.pick_lat = map_result["last_clicked"]["lat"]
        st.session_state.pick_lon = map_result["last_clicked"]["lng"]
        st.rerun()
    
    st.info(f"📍 Coordenadas: {st.session_state.pick_lat:.6f}, {st.session_state.pick_lon:.6f}")

    with st.form("form_registro"):
        titulo = st.text_input("Título del predio *")
        tipo = st.selectbox("Tipo *", ["Casa", "Apartamento", "Lote", "Finca", "Local comercial"])
        precio = st.number_input("Precio (COP) *", min_value=0, step=1000000)
        area = st.number_input("Área (m²) *", min_value=0.0)
        
        c1, c2 = st.columns(2)
        with c1: hab = st.number_input("Habitaciones", min_value=0, step=1)
        with c2: ban = st.number_input("Baños", min_value=0, step=1)
        
        direccion = st.text_input("Dirección *")
        barrio = st.text_input("Barrio / Sector")
        comisionista = st.text_input("Tu nombre *")
        whatsapp = st.text_input("Tu WhatsApp *")
        foto = st.file_uploader("Foto principal", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Guardar Predio 💾", use_container_width=True):
            if titulo and direccion and comisionista:
                foto_b64 = None
                if foto:
                    img = Image.open(foto).convert("RGB")
                    img.thumbnail((800, 800))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG")
                    foto_b64 = base64.b64encode(buf.getvalue()).decode()
                
                insert_predio({
                    "titulo": titulo, "tipo": tipo, "precio": precio, "area": area,
                    "habitaciones": hab, "banos": ban, "descripcion": "",
                    "lat": st.session_state.pick_lat, "lon": st.session_state.pick_lon,
                    "direccion": direccion, "barrio": barrio, "comisionista": comisionista,
                    "whatsapp": whatsapp, "foto_base64": foto_b64
                })
                st.success("✅ Predio guardado exitosamente")
                st.balloons()
                st.rerun()
            else:
                st.error("Completa los campos obligatorios (*)")

elif st.session_state.pagina == "mapa":
    st.markdown("### 🗺️ Mapa de la cartera")
    if len(df) > 0:
        # Usamos OpenStreetMap clásico para asegurar que se vea en la nube
        m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=14, tiles="OpenStreetMap")
        for _, row in df.iterrows():
            popup_html = f"<b>{row['titulo']}</b><br>{format_cop(row['precio'])}<br>{row['direccion']}"
            folium.Marker([row["lat"], row["lon"]], popup=folium.Popup(popup_html, max_width=200)).add_to(m)
        st_folium(m, width=None, height=500, returned_objects=[])
    else:
        st.info("No hay predios en el mapa. Registra uno o carga los ejemplos en Inicio.")

elif st.session_state.pagina == "predios":
    st.markdown("### 📋 Mis Predios")
    if len(df) == 0: 
        st.info("Tu cartera está vacía.")
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="card">
            <span class="badge-tipo">{row['tipo']}</span>
            <h4 class="card-title">{row['titulo']}</h4>
            <p class="prop-price">{format_cop(row['precio'])}</p>
            <p class="card-loc">📍 {row['direccion']} | 📐 {row['area']} m²</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones de acción dentro de la tarjeta
        c1, c2 = st.columns(2)
        msg = f"Hola, te comparto este predio:\n🏘️ {row['titulo']}\n💰 {format_cop(row['precio'])}\n📍 {row['direccion']}\n🗺️ https://www.google.com/maps?q={row['lat']},{row['lon']}"
        wa_url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        c1.link_button("📱 Compartir", wa_url, use_container_width=True)
        if c2.button("🗑️ Eliminar", key=f"del_{row['id']}", use_container_width=True):
            delete_predio(int(row["id"]))
            st.rerun()

# 6. Barra de Navegación Inferior
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
