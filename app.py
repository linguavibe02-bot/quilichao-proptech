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

# ══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL (Mobile-First)
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Quilichao PropTech",
    page_icon="🏘️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

QUILICHAO_LAT = 2.9963
QUILICHAO_LON = -76.5922

# ══════════════════════════════════════════════════════════════════════
# ESTILOS CSS - LOOK APP PREMIUM
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Forzar fuente y color de texto oscuro */
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    .stApp { background-color: #F2F4F7; color: #1E293B !important; }
    .block-container { max-width: 650px; padding-top: 1rem; padding-bottom: 4rem; }

    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] span, 
    div[data-testid="stMarkdownContainer"] h1, 
    div[data-testid="stMarkdownContainer"] h2, 
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4, p, span {
        color: #1E293B !important;
    }

    header {visibility: hidden;} footer {visibility: hidden;} #MainMenu {visibility: hidden;}

    /* Header (Naranja/Rojo original) */
    .main-header {
        background: linear-gradient(135deg, #FFC300 0%, #FF5733 50%, #C70039 100%);
        padding: 2rem 1.5rem; border-radius: 24px; color: white !important;
        text-align: center; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(199, 0, 57, 0.2);
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; font-weight: 800; color: white !important; }
    .main-header p { margin: 0.5rem 0 0 0; font-size: 1rem; color: white !important; opacity: 0.9; }

    /* MENÚ DE NAVEGACIÓN (Segmented Control - Píldoras) */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex; background-color: #E2E8F0; border-radius: 30px; padding: 4px; 
        width: 100%; margin: 0 auto 20px auto; gap: 0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child { display: none !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1; text-align: center; padding: 8px 0 !important; border-radius: 26px !important;
        margin: 0 !important; background: transparent !important; border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; cursor: pointer;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
        color: #64748B !important; font-weight: 600 !important; font-size: 13px !important; margin: 0 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #FFFFFF !important; box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p {
        color: #C70039 !important; font-weight: 800 !important;
    }

    /* Estadísticas */
    .stat-box {
        background: white; padding: 15px; border-radius: 16px;
        text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border: 1px solid #F1F5F9;
    }
    .stat-box h3 { margin: 0; font-size: 1.8rem; font-weight: 800; color: #C70039 !important; }
    .stat-box p { margin: 4px 0 0 0; font-size: 0.8rem; font-weight: 600; color: #64748B !important; text-transform: uppercase; }

    /* Tarjetas */
    .card {
        background: white; border-radius: 20px; padding: 0; overflow: hidden;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #F1F5F9;
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-3px); box-shadow: 0 12px 25px rgba(0,0,0,0.08); }
    .card img { width: 100%; height: 180px; object-fit: cover; }
    .card-body { padding: 18px; }
    
    .prop-price { color: #059669 !important; font-size: 1.4rem; font-weight: 800; margin: 5px 0; }
    .badge-tipo { background: #FEF3C7; color: #D97706 !important; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 800; text-transform: uppercase; }

    /* Botones */
    .stButton>button {
        background: linear-gradient(135deg, #FF5733 0%, #C70039 100%) !important;
        color: white !important; border: none !important; padding: 12px 20px !important; 
        border-radius: 14px !important; font-weight: 800 !important; width: 100%; 
        transition: all 0.3s !important; box-shadow: 0 4px 15px rgba(199, 0, 57, 0.25) !important;
    }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(199, 0, 57, 0.4) !important; }
    .stButton>button p { color: white !important; }

    /* Formularios y Selectbox */
    div[data-testid="stForm"] { background: white; border-radius: 20px; padding: 20px; border: 1px solid #F1F5F9; }
    div[data-baseweb="select"] > div { background-color: #F8FAFC !important; border-radius: 12px !important; border: 1px solid #E2E8F0 !important; }
    div[data-baseweb="select"] * { color: #1E293B !important; }
    .stTextInput > div > div > input { border-radius: 12px; border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# BASE DE DATOS (Lógica intacta)
# ══════════════════════════════════════════════════════════════════════
DB_FILE = "quilichao_proptech.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS predios (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, tipo TEXT NOT NULL, precio INTEGER NOT NULL, area REAL NOT NULL, habitaciones INTEGER DEFAULT 0, banos INTEGER DEFAULT 0, descripcion TEXT, lat REAL NOT NULL, lon REAL NOT NULL, direccion TEXT NOT NULL, barrio TEXT, comisionista TEXT NOT NULL, whatsapp TEXT NOT NULL, foto_base64 TEXT, fecha_registro TEXT NOT NULL)""")
    conn.commit(); conn.close()

def get_predios() -> pd.DataFrame:
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
    c = conn.cursor()
    c.execute("DELETE FROM predios WHERE id = ?", (predio_id,))
    conn.commit(); conn.close()

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

def format_cop(precio) -> str:
    try: return "$" + f"{int(precio):,}".replace(",", ".")
    except: return "$0"

init_db()

# ══════════════════════════════════════════════════════════════════════
# HEADER Y NAVEGACIÓN
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🏘️ Quilichao PropTech</h1>
    <p>Gestión inteligente para comisionistas</p>
</div>
""", unsafe_allow_html=True)

menu = st.radio(
    "Navegación",
    ["🏠 Inicio", "➕ Registrar", "🗺️ Mapa", "📋 Cartera"],
    horizontal=True,
    label_visibility="collapsed"
)

# Botón para cargar ejemplos (siempre visible en el tope si no hay datos, o en inicio)
df = get_predios()

# ══════════════════════════════════════════════════════════════════════
# VISTAS
# ══════════════════════════════════════════════════════════════════════
if menu == "🏠 Inicio":
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"""<div class="stat-box"><h3>{len(df)}</h3><p>Predios</p></div>""", unsafe_allow_html=True)
    with c2: 
        total = df["precio"].sum() if len(df) > 0 else 0
        st.markdown(f"""<div class="stat-box"><h3>{format_cop(total/1_000_000)}M</h3><p>Valor Cartera</p></div>""", unsafe_allow_html=True)

    st.markdown("### 🆕 Últimos registros")
    
    if len(df) == 0:
        st.info("Aún no tienes predios en tu cartera.")
        if st.button("📥 Cargar 5 predios de ejemplo"):
            cargar_ejemplos(); st.rerun()
    else:
        # ¡AQUÍ ESTÁ LA CORRECCIÓN! Cambiamos df.head(3) por df.iterrows() para que muestre los 5
        for _, row in df.iterrows():
            img_html = f'<img src="data:image/jpeg;base64,{row["foto_base64"]}">' if pd.notna(row["foto_base64"]) and row["foto_base64"] else '<div style="height:150px;background:#F1F5F9;display:flex;align-items:center;justify-content:center;font-size:3rem;">🏠</div>'
            
            st.markdown(f"""
            <div class="card">
                {img_html}
                <div class="card-body">
                    <span class="badge-tipo">{row['tipo']}</span>
                    <h4 style="margin: 8px 0 4px 0; font-weight: 800;">{row['titulo']}</h4>
                    <p class="prop-price">{format_cop(row['precio'])}</p>
                    <p style="font-size: 13px; color: #64748B !important;">📍 {row['direccion']}, {row['barrio']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("🔄 Recargar Ejemplos"):
            cargar_ejemplos(); st.rerun()

elif menu == "➕ Registrar":
    st.markdown("### ➕ Nuevo Predio")
    
    if "pick_lat" not in st.session_state: st.session_state.pick_lat = QUILICHAO_LAT; st.session_state.pick_lon = QUILICHAO_LON
        
    st.markdown("**📍 Toca el mapa para ubicar el predio:**")
    m_pick = folium.Map(location=[st.session_state.pick_lat, st.session_state.pick_lon], zoom_start=14)
    folium.Marker([st.session_state.pick_lat, st.session_state.pick_lon], icon=folium.Icon(color="red", icon="home", prefix="fa")).add_to(m_pick)
    map_result = st_folium(m_pick, height=250, width=None, returned_objects=["last_clicked"], key="picker")
    
    if map_result and map_result.get("last_clicked"):
        st.session_state.pick_lat, st.session_state.pick_lon = map_result["last_clicked"]["lat"], map_result["last_clicked"]["lng"]
        st.rerun()
        
    st.caption(f"📍 Coordenadas: {st.session_state.pick_lat:.6f}, {st.session_state.pick_lon:.6f}")

    with st.form("form_predio", clear_on_submit=True):
        titulo = st.text_input("Título *")
        tipo = st.selectbox("Tipo *", ["Casa", "Apartamento", "Lote", "Finca", "Local comercial", "Oficina", "Bodega"])
        c1, c2 = st.columns(2)
        with c1: precio = st.number_input("Precio (COP) *", min_value=0, step=1_000_000)
        with c2: area = st.number_input("Área (m²) *", min_value=0.0, step=1.0)
        
        direccion = st.text_input("Dirección *")
        barrio = st.text_input("Barrio / Sector")
        descripcion = st.text_area("Descripción", height=80)
        
        comisionista = st.text_input("Tu nombre *")
        whatsapp = st.text_input("WhatsApp *")
        foto = st.file_uploader("Foto principal", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Guardar Predio 💾"):
            if titulo and direccion and comisionista and whatsapp and precio > 0:
                foto_b64 = None
                if foto:
                    img = Image.open(foto).convert("RGB"); img.thumbnail((900, 900)); buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85); foto_b64 = base64.b64encode(buf.getvalue()).decode()
                
                insert_predio({
                    "titulo": titulo, "tipo": tipo, "precio": precio, "area": area, "habitaciones": 0, "banos": 0, 
                    "descripcion": descripcion, "lat": st.session_state.pick_lat, "lon": st.session_state.pick_lon,
                    "direccion": direccion, "barrio": barrio, "comisionista": comisionista, "whatsapp": whatsapp, "foto_base64": foto_b64
                })
                st.success("✅ Predio guardado exitosamente")
                st.balloons()
            else:
                st.error("❌ Completa los campos obligatorios y verifica el precio.")

elif menu == "🗺️ Mapa":
    st.markdown("### 🗺️ Mapa de la cartera")
    if len(df) > 0:
        m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=14, tiles="OpenStreetMap")
        colores = {"Casa": "blue", "Apartamento": "purple", "Lote": "green", "Finca": "darkgreen", "Local comercial": "red"}
        
        for _, row in df.iterrows():
            popup = f"<div style='font-family:Outfit;'><h4 style='color:#C70039;margin-bottom:0;'>{row['titulo']}</h4><p style='color:#059669;font-weight:bold;'>{format_cop(row['precio'])}</p><p>{row['direccion']}</p></div>"
            folium.Marker([row["lat"], row["lon"]], popup=folium.Popup(popup, max_width=250), icon=folium.Icon(color=colores.get(row["tipo"], "gray"), icon="home", prefix="fa")).add_to(m)
        st_folium(m, width=None, height=500, returned_objects=[])

elif menu == "📋 Cartera":
    st.markdown("### 📋 Mis Predios")
    if len(df) == 0: 
        st.info("Cartera vacía.")
    
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="card" style="padding: 15px;">
            <span class="badge-tipo">{row['tipo']}</span>
            <h4 style="margin: 8px 0 0 0;">{row['titulo']}</h4>
            <p class="prop-price">{format_cop(row['precio'])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("👁️ Ver ficha completa"):
            st.write(f"📍 **Dirección:** {row['direccion']}, {row['barrio']}")
            st.write(f"📐 **Área:** {row['area']} m²")
            if row['descripcion']: st.write(row['descripcion'])
            
            c1, c2 = st.columns(2)
            msg = f"Hola, te comparto este predio:\n🏘️ *{row['titulo']}*\n💰 {format_cop(row['precio'])}\n📍 {row['direccion']}\n🗺️ https://www.google.com/maps?q={row['lat']},{row['lon']}"
            
            c1.link_button("📱 WhatsApp", f"https://wa.me/?text={urllib.parse.quote(msg)}", use_container_width=True)
            if c2.button("🗑️ Eliminar", key=f"del_{row['id']}", use_container_width=True):
                delete_predio(int(row["id"])); st.rerun()
        st.write("") # Espacio
