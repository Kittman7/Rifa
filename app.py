import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random # Motor de azar para el ganador

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RIFA TIENDAPUBG", page_icon="logo (2).jpg", layout="wide")

# --- 2. ESTILOS CSS RAZER / CYBERPUNK ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@900&display=swap');

    html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }

    h1, h2, h3 {
        color: #39ff14 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
    }

    .stTextInput > div > div > input {
        background-color: #080808 !important;
        color: #39ff14 !important;
        border: 1px solid #1a1a1a !important;
    }

    /* BOTÓN REGISTRAR */
    div.stButton > button[kind="primary"] {
        background-color: transparent !important;
        border: 2px solid #39ff14 !important;
        color: #39ff14 !important;
        font-weight: 700;
        box-shadow: 0 0 5px #39ff14;
        width: 100%;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #39ff14 !important;
        color: black !important;
        box-shadow: 0 0 20px #39ff14;
    }

    /* ZONA DEL DETONADOR */
    .detonador-container {
        padding: 20px;
        border: 1px dashed #FFD700;
        border-radius: 10px;
        background-color: rgba(255, 215, 0, 0.05);
        text-align: center;
        min-height: 180px;
    }
    
    .win-btn > div > button {
        background-color: transparent !important;
        border: 2px solid #FFD700 !important;
        color: #FFD700 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        box-shadow: 0 0 15px #FFD700;
        width: 100% !important;
        height: 60px;
        margin-bottom: 20px;
    }
    .win-btn > div > button:hover {
        background-color: #FFD700 !important;
        color: black !important;
        box-shadow: 0 0 50px #FFD700 !important;
    }

    /* TEXTO DE EXPLOSIÓN DE VICTORIA */
    .winner-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px;
        color: #FFD700;
        text-shadow: 0 0 20px #FFD700, 0 0 40px #FFD700;
        animation: pulse 0.8s infinite alternate;
        text-align: center;
        margin: 10px 0;
    }
    @keyframes pulse {
      from { transform: scale(1); text-shadow: 0 0 20px #FFD700; }
      to { transform: scale(1.08); text-shadow: 0 0 50px #FFD700; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
url_hoja = "https://docs.google.com/spreadsheets/d/1YcjxsimcbJewI53VVu9exeJxQGmLCP8FkJpFA5OP5cQ/edit?gid=0#gid=0"

# Lectura forzada (ttl=0 para evitar caché)
try:
    df_ventas = conn.read(spreadsheet=url_hoja, worksheet="Ventas", ttl=0)
    df_ventas = df_ventas.dropna(how="all")
except:
    df_ventas = pd.DataFrame(columns=["Numero", "Nombre"])

try:
    df_config = conn.read(spreadsheet=url_hoja, worksheet="Config", ttl=0)
    total_guardado = int(df_config.iloc[0]["Total"]) if not df_config.empty else 150
except:
    total_guardado = 150

compradores = {int(row["Numero"]): str(row["Nombre"]).title() for _, row in df_ventas.dropna().iterrows()} if not df_ventas.empty else {}

# --- 4. INTERFAZ ---
st.markdown('<img src="https://raw.githubusercontent.com/Kittman7/Rifa/main/logo%20(2).jpg" width="150" style="border-radius: 10px; box-shadow: 0 0 15px #39ff14;">', unsafe_allow_html=True)
st.title("🎟️ RIFA TIENDAPUBG")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 REGISTRO DE VENTA")
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("ID / Nombre del Agente:")
        disponibles = [n for n in range(1, total_guardado + 1) if n not in compradores]
        numero = st.selectbox("Slot Disponible:", disponibles) if disponibles else None
        
        if st.form_submit_button("GUARDAR EN MATRIZ", type="primary"):
            if nombre.strip() == "" or not numero:
                st.error("⚠️ Datos incompletos.")
            else:
                nuevo_dato = pd.DataFrame([{"Numero": numero, "Nombre": nombre.strip().title()}])
                df_act = pd.concat([df_ventas, nuevo_dato], ignore_index=True)
                conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_act)
                st.success(f"Slot {numero} sincronizado.")
                st.rerun()

with col2:
    st.subheader("🔍 BUSCADOR DE PARTICIPANTES")
    busqueda = st.text_input("Escanear por ID o Nombre:")
    if busqueda:
        if busqueda.isdigit() and int(busqueda) in compradores:
            st.success(f"✅ Slot {busqueda}: {compradores[int(busqueda)]}")
        elif not busqueda.isdigit():
            encontrados = [f"{n}" for n, p in compradores.items() if busqueda.lower() in p.lower()]
            if encontrados: st.success(f"👤 {busqueda.title()} tiene: {', '.join(encontrados)}")

    st.write("")
    # ZONA DE PREMIACIÓN (DETONADOR)
    st.markdown('<div class="detonador-container">', unsafe_allow_html=True)
    st.write("✨ **ZONA DE PREMIACIÓN** ✨")
    
    st.markdown('<div class="win-btn">', unsafe_allow_html=True)
    detonar = st.button("🏆 ¡DETONAR GANADOR!", type="secondary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # LÓGICA DE DETONACIÓN AUTOMÁTICA
    if detonar:
        if compradores:
            # Selecciona un número ganador al azar de los vendidos
            num_ganador = random.choice(list(compradores.keys()))
            nombre_ganador = compradores[num_ganador]
            # Guardamos en la memoria de la sesión
            st.session_state['ganador_actual'] = f"💥 {nombre_ganador.upper()} 💥"
            st.session_state['slot_actual'] = f"GANADOR DEL SLOT: {num_ganador}"
        else:
            st.session_state['ganador_actual'] = "SIN PARTICIPANTES"
            st.session_state['slot_actual'] = ""

    # Mostrar ganador si existe en memoria
    if 'ganador_actual' in st.session_state:
        st.markdown(f'<p class="winner-text">{st.session_state["ganador_actual"]}</p>', unsafe_allow_html=True)
        if st.session_state['slot_actual']:
            st.markdown(f'<p style="color:#FFD700; font-weight:bold; font-size:20px;">{st.session_state["slot_actual"]}</p>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. TABLERO VISUAL ---
st.write("---")
st.subheader("📊 ESTADO DE LA MATRIZ")
grid_html = '<style>.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(60px,1fr));gap:10px;}.box{display:flex;align-items:center;justify-content:center;font-weight:700;padding:15px;border-radius:4px;border:1px solid;}.dispo{background:rgba(57,255,20,0.1);color:#39ff14;border-color:#39ff14;}.ocu{background:rgba(255,57,57,0.2);color:#ff3939;border-color:#ff3939;}</style><div class="grid">'
for i in range(1, total_guardado + 1):
    grid_html += f'<div class="box {"ocu" if i in compradores else "dispo"}">{i}</div>'
st.markdown(grid_html + '</div>', unsafe_allow_html=True)
