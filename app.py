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

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Quilichao PropTech",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# ESTILOS CSS ORIGINALES (Los que ya te gustaban)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .main-header { background: linear-gradient(135deg, #FFC300 0%, #FF5733 50%, #C70039 100%); padding: 2rem 1.5rem; border-radius: 18px; color: white; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 8px 25px rgba(199, 0, 57, 0.25); }
    .main-header h1 { margin: 0; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.5px; }
    .main-header p { margin: 0.5rem 0 0 0; font-size: 1.05rem; opacity: 0.95; }
    .stat-box { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 1.3rem; border-radius: 14px; text-align: center; box-shadow: 0 4px 15px rgba(30, 60, 114, 0.2); }
    .stat-box h3 { margin: 0; font-size: 2.2rem; font-weight: 800; }
    .stat-box p { margin: 0.3rem 0 0 0; font-size: 0.9rem; opacity: 0.95; }
    .prop-price { color: #C70039; font-size: 1.5rem; font-weight: 800; }
    .badge-tipo { display: inline-block; background: #FFC300; color: #1a1a1a; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }
    .stButton>button { background: linear-gradient(135deg, #FF5733 0%, #C70039 100%); color: white; border: none; padding: 0.55rem 1.5rem; border-radius: 10px; font-weight: 700; transition: all 0.2s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(199, 0, 57, 0.35); }
    div[data-testid="stMetricValue"] { color: #C70039; font-weight: 800; }
    .footer-note { text-align: center; color: #888; font-size: 0.8rem; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BASE DE DATOS (SQLite)
# ==============================================================================
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
    c.execute("""INSERT INTO predios (titulo, tipo, precio, area, habitaciones, banos, descripcion, lat, lon, direccion, barrio, comisionista, whatsapp, foto_base64, fecha_registro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (d["titulo"], d["tipo"], d["precio"], d["area"], d["habitaciones"], d["banos"], d["descripcion"], d["lat"], d["lon"], d["direccion"], d["barrio"], d["comisionista"], d["whatsapp"], d["foto_base64"], datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

def delete_predio(predio_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM predios WHERE id = ?", (predio_id,))
    conn.commit(); conn.close()

def cargar_ejemplos():
    # Aquí están los 5 ejemplos originales intactos
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

# ==============================================================================
# INTERFAZ PRINCIPAL
# ==============================================================================
st.markdown('<div class="main-header"><h1>🏘️ Quilichao PropTech</h1><p>La herramienta SIG + CRM para comisionistas de Santander de Quilichao</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧭 Navegación")
    menu = st.radio("Ir a:", ["🏠 Inicio", "➕ Registrar Predio", "🗺️ Ver Mapa", "📋 Mis Predios"], label_visibility="collapsed")
    st.divider()
    df_side = get_predios()
    st.markdown("### 📊 Tu cartera")
    st.metric("Predios registrados", len(df_side))
    if len(df_side) > 0: st.metric("Valor total", format_cop(df_side["precio"].sum()))
    st.divider()
    st.markdown("### 🧪 Para pruebas")
    if st.button("📥 Cargar datos de ejemplo", use_container_width=True):
        cargar_ejemplos(); st.success("✅ 5 predios de ejemplo cargados"); st.rerun()
    st.divider()
    st.caption("**Fase 1 · MVP**\nSIG + Ficha de predio\nQuilichao, Cauca 🇨🇴")

# ==============================================================================
# VISTAS
# ==============================================================================
if menu == "🏠 Inicio":
    df = get_predios()
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"""<div class="stat-box"><h3>{len(df)}</h3><p>Predios en cartera</p></div>""", unsafe_allow_html=True)
    with c2: 
        total = df["precio"].sum() if len(df) > 0 else 0
        st.markdown(f"""<div class="stat-box"><h3>{format_cop(total/1_000_000)}M</h3><p>Valor cartera</p></div>""", unsafe_allow_html=True)
    with c3:
        tipos = df["tipo"].nunique() if len(df) > 0 else 0
        st.markdown(f"""<div class="stat-box"><h3>{tipos}</h3><p>Tipos de predio</p></div>""", unsafe_allow_html=True)
    with c4:
        barrios = df["barrio"].nunique() if len(df) > 0 else 0
        st.markdown(f"""<div class="stat-box"><h3>{barrios}</h3><p>Sectores cubiertos</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("👋 Bienvenido a tu herramienta profesional")
    st.markdown("Esta app está diseñada para **comisionistas independientes** de Santander de Quilichao y el norte del Cauca.")
    if len(df) > 0:
        st.subheader("🆕 Últimos predios registrados")
        for _, row in df.head(3).iterrows():
            with st.container():
                c_img, c_info = st.columns([1, 3])
                with c_img:
                    if pd.notna(row["foto_base64"]) and row["foto_base64"]: st.image(base64.b64decode(row["foto_base64"]), use_container_width=True)
                    else: st.markdown("<div style='background:#eee;height:130px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2rem;'>🏠</div>", unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"#### {row['titulo']} <span class='badge-tipo'>{row['tipo']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='prop-price'>{format_cop(row['precio'])}</span>", unsafe_allow_html=True)
                    st.caption(f"📍 {row['direccion']}, {row['barrio']} · 📐 {row['area']} m²")
            st.divider()

elif menu == "➕ Registrar Predio":
    st.subheader("➕ Registrar nuevo predio")
    if "pick_lat" not in st.session_state: st.session_state.pick_lat = 2.9963; st.session_state.pick_lon = -76.5922
    col_form, col_map = st.columns([1, 1])
    with col_map:
        st.markdown("**📍 Haz clic en el mapa para ubicar el predio**")
        m_pick = folium.Map(location=[st.session_state.pick_lat, st.session_state.pick_lon], zoom_start=14)
        folium.Marker([st.session_state.pick_lat, st.session_state.pick_lon], icon=folium.Icon(color="red", icon="home", prefix="fa")).add_to(m_pick)
        map_result = st_folium(m_pick, height=380, width=None, returned_objects=["last_clicked"], key="picker_map")
        if map_result and map_result.get("last_clicked"):
            clat, clon = map_result["last_clicked"]["lat"], map_result["last_clicked"]["lng"]
            if abs(clat - st.session_state.pick_lat) > 1e-6 or abs(clon - st.session_state.pick_lon) > 1e-6:
                st.session_state.pick_lat, st.session_state.pick_lon = clat, clon; st.rerun()
        st.info(f"📍 **Lat:** `{st.session_state.pick_lat:.6f}` · **Lon:** `{st.session_state.pick_lon:.6f}`")
    with col_form:
        with st.form("form_predio", clear_on_submit=True):
            titulo = st.text_input("Título *"); tipo = st.selectbox("Tipo *", ["Casa", "Apartamento", "Lote", "Finca", "Local comercial", "Oficina", "Bodega"])
            precio = st.number_input("Precio (COP) *", min_value=0, step=1_000_000, format="%d"); area = st.number_input("Área (m²) *", min_value=0.0, step=1.0)
            c1, c2 = st.columns(2)
            with c1: habitaciones = st.number_input("Habitaciones", min_value=0, step=1)
            with c2: banos = st.number_input("Baños", min_value=0, step=1)
            direccion = st.text_input("Dirección *"); barrio = st.text_input("Barrio / Sector"); descripcion = st.text_area("Descripción", height=80)
            comisionista = st.text_input("Tu nombre *"); whatsapp = st.text_input("WhatsApp *"); foto = st.file_uploader("Foto principal", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("💾 Guardar Predio", use_container_width=True):
                if not titulo or not direccion or not comisionista or not whatsapp or precio <= 0: st.error("❌ Completa los campos obligatorios (*) y verifica el precio.")
                else:
                    foto_b64 = None
                    if foto:
                        img = Image.open(foto).convert("RGB"); img.thumbnail((900, 900)); buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85); foto_b64 = base64.b64encode(buf.getvalue()).decode()
                    insert_predio({"titulo": titulo, "tipo": tipo, "precio": precio, "area": area, "habitaciones": habitaciones, "banos": banos, "descripcion": descripcion, "lat": st.session_state.pick_lat, "lon": st.session_state.pick_lon, "direccion": direccion, "barrio": barrio, "comisionista": comisionista, "whatsapp": whatsapp, "foto_base64": foto_b64})
                    st.success(f"✅ Predio **{titulo}** registrado exitosamente"); st.balloons()

elif menu == "🗺️ Ver Mapa":
    st.subheader("🗺️ Mapa de tu cartera")
    df = get_predios()
    if len(df) == 0: st.info("📭 Aún no tienes predios registrados.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1: tipos_sel = st.multiselect("Filtrar por tipo:", sorted(df["tipo"].unique()), default=sorted(df["tipo"].unique()))
        with f2: max_m = int(df["precio"].max() / 1_000_000) + 5; rango = st.slider("Rango precio (millones COP):", 0, max_m, (0, max_m))
        with f3: texto = st.text_input("Buscar por título:", "")
        df_f = df[df["tipo"].isin(tipos_sel) & (df["precio"] >= rango[0]*1_000_000) & (df["precio"] <= rango[1]*1_000_000)]
        if texto: df_f = df_f[df_f["titulo"].str.contains(texto, case=False, na=False)]
        st.caption(f"Mostrando **{len(df_f)}** de **{len(df)}** predios")
        centro = [df_f["lat"].mean(), df_f["lon"].mean()] if len(df_f) > 0 else [2.9963, -76.5922]
        m = folium.Map(location=centro, zoom_start=14)
        colores = {"Casa": "blue", "Apartamento": "purple", "Lote": "green", "Finca": "darkgreen", "Local comercial": "red", "Oficina": "orange", "Bodega": "darkred"}
        for _, row in df_f.iterrows():
            popup = f"<div style='font-family:Arial;min-width:200px;'><h4>{row['titulo']}</h4><p><b>Precio:</b> {format_cop(row['precio'])}</p><p><b>Tipo:</b> {row['tipo']}</p><p><b>Área:</b> {row['area']} m²</p><p><b>Ubicación:</b> {row['direccion']}</p><p><b>WhatsApp:</b> {row['whatsapp']}</p></div>"
            folium.Marker([row["lat"], row["lon"]], popup=folium.Popup(popup, max_width=300), icon=folium.Icon(color=colores.get(row["tipo"], "gray"), icon="home", prefix="fa")).add_to(m)
        st_folium(m, width=None, height=600, returned_objects=[])

elif menu == "📋 Mis Predios":
    st.subheader("📋 Gestión de predios")
    df = get_predios()
    if len(df) == 0: st.info("📭 Aún no tienes predios registrados.")
    else:
        st.caption(f"Tienes **{len(df)}** predios en cartera.")
        for _, row in df.iterrows():
            with st.container():
                c_img, c_info, c_acc = st.columns([1, 3, 1])
                with c_img:
                    if pd.notna(row["foto_base64"]) and row["foto_base64"]: st.image(base64.b64decode(row["foto_base64"]), use_container_width=True)
                    else: st.markdown("<div style='background:#f0f0f0;height:120px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;'>🏠</div>", unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"#### {row['titulo']} <span class='badge-tipo'>{row['tipo']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='prop-price'>{format_cop(row['precio'])}</span>", unsafe_allow_html=True)
                    hab = int(row["habitaciones"]) if pd.notna(row["habitaciones"]) else 0; ban = int(row["banos"]) if pd.notna(row["banos"]) else 0
                    extras = f" · 🛏️ {hab} hab · 🚿 {ban} baños" if hab or ban else ""
                    st.caption(f"📍 {row['direccion']}, {row['barrio'] or '—'} · 📐 {row['area']} m²{extras}")
                    with st.expander("👁️ Ver ficha completa"):
                        if row["descripcion"]: st.write(row["descripcion"])
                        st.write(f"**Comisionista:** {row['comisionista']} | **WhatsApp:** {row['whatsapp']}")
                        st.write(f"**Coordenadas:** {row['lat']:.6f}, {row['lon']:.6f} | **Registrado:** {row['fecha_registro']}")
                with c_acc:
                    msg = f"Hola, te comparto este predio:\n\n🏘️ *{row['titulo']}*\n💰 {format_cop(row['precio'])}\n📐 {row['area']} m²\n📍 {row['direccion']}, {row['barrio'] or ''}\n🗺️ https://www.google.com/maps?q={row['lat']},{row['lon']}"
                    st.link_button("📱 WhatsApp", f"https://wa.me/?text={urllib.parse.quote(msg)}", use_container_width=True)
                    if st.button("🗑️ Eliminar", key=f"del_{row['id']}", use_container_width=True): delete_predio(int(row["id"])); st.rerun()
                st.divider()
