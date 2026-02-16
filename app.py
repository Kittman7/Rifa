import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RIFA TIENDAPUBG", page_icon="logo (2).jpg", layout="wide")

# --- 2. ESTILOS CSS RAZER / CYBERPUNK ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@900&display=swap');

    html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }

    .section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 15px; }
    .mini-logo { width: 35px; height: 35px; border-radius: 6px; box-shadow: 0 0 8px #39ff14; border: 1px solid #39ff14; }

    h1, h2, h3 {
        color: #39ff14 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
        margin: 0 !important;
    }

    .stTextInput > div > div > input {
        background-color: #080808 !important;
        color: #39ff14 !important;
        border: 1px solid #1a1a1a !important;
    }

    /* BOTONES */
    div.stButton > button[kind="primary"] {
        background-color: transparent !important;
        border: 2px solid #39ff14 !important;
        color: #39ff14 !important;
        font-weight: 700;
        text-transform: uppercase;
        box-shadow: 0 0 5px #39ff14;
        width: 100%;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #39ff14 !important;
        color: black !important;
        box-shadow: 0 0 20px #39ff14;
    }

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
        text-transform: uppercase;
        box-shadow: 0 0 15px #FFD700;
        width: 100% !important;
        height: 60px;
    }

    @keyframes explode-enter {
        0% { transform: scale(0.5); opacity: 0; }
        50% { transform: scale(1.2); opacity: 1; text-shadow: 0 0 50px #FFD700; }
        100% { transform: scale(1); opacity: 1; text-shadow: 0 0 20px #FFD700; }
    }

    .winner-text-explosion {
        font-family: 'Orbitron', sans-serif;
        font-size: 42px;
        color: #FFD700;
        text-align: center;
        animation: explode-enter 1s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN A DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
url_hoja = "https://docs.google.com/spreadsheets/d/1YcjxsimcbJewI53VVu9exeJxQGmLCP8FkJpFA5OP5cQ/edit?gid=0#gid=0"

# Lectura segura
try:
    df_ventas = conn.read(spreadsheet=url_hoja, worksheet="Ventas", ttl=0)
    df_ventas = df_ventas.dropna(how="all")
    # Limpieza técnica: asegurar que Numero sea entero
    if not df_ventas.empty:
        df_ventas['Numero'] = pd.to_numeric(df_ventas['Numero'], errors='coerce')
        df_ventas = df_ventas.dropna(subset=['Numero'])
except Exception:
    df_ventas = pd.DataFrame(columns=["Numero", "Nombre"])

try:
    df_config = conn.read(spreadsheet=url_hoja, worksheet="Config", ttl=0)
    total_guardado = int(df_config.iloc[0]["Total"]) if not df_config.empty else 150
except Exception:
    total_guardado = 150

compradores = {int(row["Numero"]): str(row["Nombre"]).title() for _, row in df_ventas.iterrows()} if not df_ventas.empty else {}

# --- 4. INTERFAZ ---
logo_url = "https://raw.githubusercontent.com/Kittman7/Rifa/main/logo%20(2).jpg"
st.markdown(f'<img src="{logo_url}" width="150" style="border-radius: 10px; box-shadow: 0 0 15px #39ff14;">', unsafe_allow_html=True)
st.title("RIFA TIENDAPUBG")

col1, col2 = st.columns([1, 1])
mini_logo_html = f'<img src="{logo_url}" class="mini-logo">'

with col1:
    # REGISTRO DE JUGADOR (Sin logo arriba)
    st.markdown('<div class="section-header"><h3>REGISTRO DE JUGADOR</h3></div>', unsafe_allow_html=True)
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("ID / Nombre del Agente:")
        disponibles = [n for n in range(1, total_guardado + 1) if n not in compradores]
        numero = st.selectbox("Slot Disponible:", disponibles) if disponibles else None
        
        if st.form_submit_button("GUARDAR EN MATRIZ", type="primary"):
            if nombre.strip() == "" or not numero:
                st.error("⚠️ Datos incompletos.")
            else:
                try:
                    nuevo_dato = pd.DataFrame([{"Numero": numero, "Nombre": nombre.strip().title()}])
                    df_act = pd.concat([df_ventas, nuevo_dato], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_act) #
                    st.rerun()
                except Exception:
                    st.error("❌ Error de permisos. Verifica que el Bot sea 'Editor' en Google Sheets.") #

with col2:
    # BUSCADOR DE PARTICIPANTES (Sin logo arriba)
    st.markdown('<div class="section-header"><h3>BUSCADOR DE PARTICIPANTES</h3></div>', unsafe_allow_html=True)
    buscado_nombre, buscado_numeros = None, []
    busqueda = st.text_input("Escanear por ID o Nombre:")
    
    if busqueda:
        nombre_e = None
        if busqueda.isdigit() and int(busqueda) in compradores:
            nombre_e = compradores[int(busqueda)]
        if not nombre_e:
             for num, nom in compradores.items():
                 if busqueda.lower() in nom.lower():
                     nombre_e = nom
                     break
        if nombre_e:
            buscado_nombre = nombre_e
            buscado_numeros = [str(n) for n, nom in compradores.items() if nom == nombre_e]
            st.success(f"✅ **{buscado_nombre}** tiene los números: **{', '.join(buscado_numeros)}**")

    st.write("")
    st.markdown('<div class="detonador-container">', unsafe_allow_html=True)
    st.write("✨ **ZONA DE PREMIACIÓN** ✨")
    
    # Detonador con animación de felicidad
    if st.button("🏆 ¡DETONAR GANADOR!", type="secondary", use_container_width=True):
        if buscado_nombre:
            st.session_state['ganador_ok'] = f"💥 {buscado_nombre.upper()} 💥"
            st.session_state['nums_ok'] = f"NÚMEROS GANADORES: {', '.join(buscado_numeros)}"
            st.balloons()
        else:
            st.warning("⚠️ Busca a un participante para detonarlo.")

    if 'ganador_ok' in st.session_state:
        st.markdown(f'<p class="winner-text-explosion">{st.session_state["ganador_ok"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#FFD700; font-weight:bold; font-size:20px; text-align:center;">{st.session_state["nums_ok"]}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. TABLERO ---
st.write("---")
# NUMEROS DE RIFA (Con logo abajo)
st.markdown(f'<div class="section-header">{mini_logo_html}<h3>NUMEROS DE RIFA</h3></div>', unsafe_allow_html=True)
grid_html = '<style>.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(60px,1fr));gap:10px;}.box{display:flex;align-items:center;justify-content:center;font-weight:700;padding:15px;border-radius:4px;border:1px solid;}.dispo{background:rgba(57,255,20,0.1);color:#39ff14;border-color:#39ff14;box-shadow:0 0 5px #39ff14;}.ocu{background:rgba(255,57,57,0.2);color:#ff3939;border-color:#ff3939;}</style><div class="grid">'
for i in range(1, total_guardado + 1):
    grid_html += f'<div class="box {"ocu" if i in compradores else "dispo"}">{i}</div>'
st.markdown(grid_html + '</div>', unsafe_allow_html=True)
