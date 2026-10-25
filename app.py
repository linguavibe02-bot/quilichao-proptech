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
# CONFIGURACIÓN GENERAL
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
# ESTILOS CSS - LOOK INMOBILIARIA (ZILLOW STYLE)
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #F8FAFC; color: #1E293B !important; }
    .block-container { max-width: 700px; padding-top: 1rem; padding-bottom: 4rem; }

    header {visibility: hidden;} footer {visibility: hidden;} #MainMenu {visibility: hidden;}

    /* 1. Header tipo Lujo */
    .main-header {
        background: #0F172A; padding: 2.5rem 1.5rem; border-radius: 20px; color: white !important;
        text-align: center; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);
    }
    .main-header h1 { 
        margin: 0; font-family: 'Playfair Display', serif; font-size: 2.6rem; 
        font-weight: 700; color: #FFFFFF !important; letter-spacing: -0.5px;
    }
    .main-header p { 
        margin: 8px 0 0 0; font-size: 0.85rem; color: #94A3B8 !important; 
        text-transform: uppercase; letter-spacing: 2px; font-weight: 600;
    }

    /* 2. PESTAÑAS (TABS) - Estilo Zillow/Redfin */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; background-color: transparent; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent; border: none; padding: 0 10px;
        font-weight: 600; font-size: 15px; color: #64748B;
    }
    /* Pestaña activa */
    .stTabs [aria-selected="true"] {
        color: #0F172A !important; font-weight: 800 !important;
        border-bottom: 3px solid #0F172A !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #0F172A; }

    /* 3. Tarjetas de Propiedades */
    .card {
        background: white; border-radius: 16px; padding: 0; overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px; 
        border: 1px solid #E2E8F0; transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-3px); box-shadow: 0 12px 20px -5px rgba(15, 23, 42, 0.1); }
    .card-img { width: 100%; height: 200px; object-fit: cover; }
    .card-body { padding: 20px; }
    
    .prop-title { 
        font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 700; 
        margin: 8px 0 4px 0; color: #0F172A !important;
    }
    .prop-price { color: #059669 !important; font-size: 1.5rem; font-weight: 800; margin: 5px 0 10px 0; }
    .badge-tipo { 
        background: #F1F5F9; color: #0F172A !important; padding: 5px 12px; 
        border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
    }
    .card-text { font-size: 14px; color: #475569 !important; margin: 0; }

    /* 4. Botones y Formularios */
    .stButton>button {
        background: #0F172A !important; color: white !important; border: none !important; 
        padding: 12px 20px !important; border-radius: 10px !important; font-weight: 600 !important; 
        width: 100%; transition: all 0.2s !important;
    }
    .stButton>button:hover { background: #1E293B !important; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.3) !important; }
    .stButton>button p { color: white !important; }

    div[data-testid="stForm"] { background: white; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; }
    div[data-baseweb="select"] > div { background-color: #F8FAFC !important; border-radius: 10px !important; border: 1px solid #E2E8F0 !important; }
    div[data-baseweb="select"] * { color: #1E293B !important; }
    .stTextInput > div > div > input { border-radius: 10px; border: 1px solid #E2E8F0; }

    /* 5. Estadísticas */
    .stat-box {
        background: white; padding: 20px; border-radius: 16px; text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
    }
    .stat-box h3 { font-family: 'Playfair Display', serif; margin: 0; font-size: 2rem; color: #0F172A !important; }
    .stat-box p { margin: 4px 0 0 0; font-size: 0.8rem; font-weight: 600; color: #64748B !important; text-transform: uppercase; letter-spacing: 1px;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# BASE DE DATOS (Intacta)
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
# HEADER
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <p>Quilichao, Cauca</p>
    <h1>PropTech</h1>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PESTAÑAS (REEMPLAZA AL MENÚ DE PÍLDORAS)
# ══════════════════════════════════════════════════════════════════════
tab_inicio, tab_registrar, tab_mapa, tab_cartera = st.tabs([
    "🏠 Inicio", "➕ Registrar", "🗺️ Mapa", "📋 Cartera"
])

df = get_predios()

# ══════════════════════════════════════════════════════════════════════
# VISTA 1: INICIO
# ══════════════════════════════════════════════════════════════════════
with tab_inicio:
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"""<div class="stat-box"><h3>{len(df)}</h3><p>Propiedades</p></div>""", unsafe_allow_html=True)
    with c2: 
        total = df["precio"].sum() if len(df) > 0 else 0
        st.markdown(f"""<div class="stat-box"><h3>{format_cop(total/1_000_000)}M</h3><p>Valor Cartera</p></div>""", unsafe_allow_html=True)

    st.markdown("### Propiedades Destacadas")
    
    if len(df) == 0:
        st.info("Aún no tienes propiedades. Carga las de ejemplo.")
        if st.button("📥 Cargar Propiedades de Ejemplo"):
            cargar_ejemplos(); st.rerun()
    else:
        for _, row in df.iterrows():
            img_html = f'<img src="data:image/jpeg;base64,{row["foto_base64"]}" class="card-img">' if pd.notna(row["foto_base64"]) and row["foto_base64"] else '<div class="card-img" style="background:#E2E8F0;display:flex;align-items:center;justify-content:center;font-size:3rem;">🏠</div>'
            
            st.markdown(f"""
            <div class="card">
                {img_html}
                <div class="card-body">
                    <span class="badge-tipo">{row['tipo']}</span>
                    <div class="prop-title">{row['titulo']}</div>
                    <div class="prop-price">{format_cop(row['precio'])}</div>
                    <p class="card-text">📍 {row['direccion']}, {row['barrio']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("🔄 Recargar Ejemplos"):
            cargar_ejemplos(); st.rerun()

# ══════════════════════════════════════════════════════════════════════
# VISTA 2: REGISTRAR
# ══════════════════════════════════════════════════════════════════════
with tab_registrar:
    st.markdown("<h3 style='font-family:Playfair Display; color:#0F172A;'>Registrar Propiedad</h3>", unsafe_allow_html=True)
    
    if "pick_lat" not in st.session_state: st.session_state.pick_lat = QUILICHAO_LAT; st.session_state.pick_lon = QUILICHAO_LON
        
    st.markdown("**📍 Toca el mapa para ubicar la propiedad:**")
    m_pick = folium.Map(location=[st.session_state.pick_lat, st.session_state.pick_lon], zoom_start=14, tiles="OpenStreetMap")
    folium.Marker([st.session_state.pick_lat, st.session_state.pick_lon], icon=folium.Icon(color="darkblue", icon="home", prefix="fa")).add_to(m_pick)
    map_result = st_folium(m_pick, height=250, width=None, returned_objects=["last_clicked"], key="picker")
    
    if map_result and map_result.get("last_clicked"):
        st.session_state.pick_lat, st.session_state.pick_lon = map_result["last_clicked"]["lat"], map_result["last_clicked"]["lng"]
        st.rerun()
        
    st.caption(f"📍 Coordenadas: {st.session_state.pick_lat:.6f}, {st.session_state.pick_lon:.6f}")

    with st.form("form_predio", clear_on_submit=True):
        titulo = st.text_input("Título de la propiedad *")
        tipo = st.selectbox("Tipo de inmueble *", ["Casa", "Apartamento", "Lote", "Finca", "Local comercial", "Oficina", "Bodega"])
        c1, c2 = st.columns(2)
        with c1: precio = st.number_input("Precio (COP) *", min_value=0, step=1_000_000)
        with c2: area = st.number_input("Área (m²) *", min_value=0.0, step=1.0)
        
        direccion = st.text_input("Dirección *")
        barrio = st.text_input("Barrio / Sector")
        descripcion = st.text_area("Descripción", height=80)
        
        comisionista = st.text_input("Nombre del comisionista *")
        whatsapp = st.text_input("WhatsApp *")
        foto = st.file_uploader("Foto principal", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Guardar Propiedad 💾"):
            if titulo and direccion and comisionista and whatsapp and precio > 0:
                foto_b64 = None
                if foto:
                    img = Image.open(foto).convert("RGB"); img.thumbnail((900, 900)); buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85); foto_b64 = base64.b64encode(buf.getvalue()).decode()
                
                insert_predio({
                    "titulo": titulo, "tipo": tipo, "precio": precio, "area": area, "habitaciones": 0, "banos": 0, 
                    "descripcion": descripcion, "lat": st.session_state.pick_lat, "lon": st.session_state.pick_lon,
                    "direccion": direccion, "barrio": barrio, "comisionista": comisionista, "whatsapp": whatsapp, "foto_base64": foto_b64
                })
                st.success("✅ Propiedad registrada exitosamente")
                st.balloons()
            else:
                st.error("❌ Completa los campos obligatorios y verifica el precio.")

# ══════════════════════════════════════════════════════════════════════
# VISTA 3: MAPA
# ══════════════════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown("<h3 style='font-family:Playfair Display; color:#0F172A;'>Mapa de Propiedades</h3>", unsafe_allow_html=True)
    if len(df) > 0:
        m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=14, tiles="OpenStreetMap")
        colores = {"Casa": "darkblue", "Apartamento": "cadetblue", "Lote": "darkgreen", "Finca": "green", "Local comercial": "darkred"}
        
        for _, row in df.iterrows():
            popup = f"<div style='font-family:Inter;'><h4 style='font-family:Playfair Display; color:#0F172A; margin-bottom:5px;'>{row['titulo']}</h4><p style='color:#059669;font-weight:bold; font-size:16px; margin:0;'>{format_cop(row['precio'])}</p><p style='color:#64748B; margin:5px 0 0 0;'>{row['direccion']}</p></div>"
            folium.Marker([row["lat"], row["lon"]], popup=folium.Popup(popup, max_width=250), icon=folium.Icon(color=colores.get(row["tipo"], "gray"), icon="home", prefix="fa")).add_to(m)
        st_folium(m, width=None, height=500, returned_objects=[])

# ══════════════════════════════════════════════════════════════════════
# VISTA 4: CARTERA
# ══════════════════════════════════════════════════════════════════════
with tab_cartera:
    st.markdown("<h3 style='font-family:Playfair Display; color:#0F172A;'>Mi Cartera</h3>", unsafe_allow_html=True)
    if len(df) == 0: 
        st.info("Tu cartera está vacía.")
    
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="card" style="padding: 20px;">
            <span class="badge-tipo">{row['tipo']}</span>
            <div class="prop-title">{row['titulo']}</div>
            <div class="prop-price">{format_cop(row['precio'])}</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Ver detalles y compartir"):
            st.write(f"📍 **Dirección:** {row['direccion']}, {row['barrio']}")
            st.write(f"📐 **Área:** {row['area']} m²")
            if row['descripcion']: st.write(row['descripcion'])
            
            c1, c2 = st.columns(2)
            msg = f"Hola, te comparto esta propiedad:\n🏘️ *{row['titulo']}*\n💰 {format_cop(row['precio'])}\n📍 {row['direccion']}\n🗺️ https://www.google.com/maps?q={row['lat']},{row['lon']}"
            
            c1.link_button("📱 Compartir", f"https://wa.me/?text={urllib.parse.quote(msg)}", use_container_width=True)
            if c2.button("🗑️ Eliminar", key=f"del_{row['id']}", use_container_width=True):
                delete_predio(int(row["id"])); st.rerun()
        st.write("") 
