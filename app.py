import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA Y TEMA GAMER ---
st.set_page_config(page_title="Rifa Cyberpunk", page_icon="logo (2).jpg", layout="wide")

# INYECCIÓN DE CSS ESTILO RAZER/CYBERPUNK
st.markdown("""
<style>
    /* Importar fuente futurista de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

    /* Aplicar la fuente a toda la app */
    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
    }

    /* --- ESTILO DE TÍTULOS --- */
    h1, h2, h3 {
        color: #39ff14 !important; /* Verde neón para títulos */
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.5); /* Resplandor verde suave */
    }

    /* --- ESTILO DE INPUTS Y SELECTBOXES --- */
    /* Fondo negro, texto blanco y borde verde neón al enfocar */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div {
        background-color: #080808 !important;
        color: #39ff14 !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 4px;
    }
    /* Efecto foco (cuando haces clic para escribir) */
    .stTextInput > div > div > input:focus, 
    .stSelectbox > div > div > div:focus-within {
        border-color: #39ff14 !important;
        box-shadow: 0 0 10px #39ff14 !important; /* Glow intenso */
    }
    /* Color de las etiquetas de los inputs */
    .stTextInput label, .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600;
    }

    /* --- ESTILO DE BOTONES (Primary) --- */
    /* Botones con borde neón y fondo transparente inicialmente */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: transparent !important;
        border: 2px solid #39ff14 !important;
        color: #39ff14 !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 0 5px #39ff14;
    }
    /* Efecto Hover (al pasar el mouse) intenso */
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #39ff14 !important;
        color: black !important;
        box-shadow: 0 0 20px #39ff14, 0 0 40px #39ff14 !important; /* DOBLE GLOW */
    }
    
     /* --- ESTILO DE BOTONES (Secondary - como el de borrar) --- */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #1a1a1a !important;
        border: 1px solid #39ff14 !important;
        color: #ffffff !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #ff3939 !important; /* Rojo al pasar el mouse para borrar */
        color: #ff3939 !important;
        box-shadow: 0 0 15px #ff3939 !important;
    }

    /* --- ESTILO DE ALERTAS (Success, Error, Warning) --- */
    .stAlert {
        background-color: #0e0e0e !important;
        border: 1px solid;
    }
    div[data-baseweb="notification"][kind="success"] { border-color: #39ff14 !important; }
    div[data-baseweb="notification"][kind="error"] { border-color: #ff3939 !important; }
    div[data-baseweb="notification"][kind="warning"] { border-color: #ffff00 !important; }

    /* --- ESTILO DE LA BARRA LATERAL --- */
    section[data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 1px solid #39ff14;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Tu enlace real de Google Sheets:
url_hoja = "https://docs.google.com/spreadsheets/d/1YcjxsimcbJewI53VVu9exeJxQGmLCP8FkJpFA5OP5cQ/edit?gid=0#gid=0"

# --- LEER DATOS GUARDADOS ---
try:
    df_ventas = conn.read(spreadsheet=url_hoja, worksheet="Ventas", ttl=0)
    df_ventas = df_ventas.dropna(how="all")
except Exception:
    df_ventas = pd.DataFrame(columns=["Numero", "Nombre"])

try:
    df_config = conn.read(spreadsheet=url_hoja, worksheet="Config", ttl=0)
    df_config = df_config.dropna(how="all")
    total_guardado = int(df_config.iloc[0]["Total"]) if not df_config.empty else 150
except Exception:
    total_guardado = 150

# --- PROCESAR LOS DATOS ---
compradores = {}
if not df_ventas.empty and "Numero" in df_ventas.columns:
    for index, row in df_ventas.dropna(subset=["Numero", "Nombre"]).iterrows():
        compradores[int(row["Numero"])] = str(row["Nombre"]).title()

# --- INTERFAZ VISUAL PRINCIPAL ---

# Logo principal con un pequeño efecto de resplandor
st.markdown('<img src="https://raw.githubusercontent.com/Kittman7/Rifa/main/logo%20(2).jpg" width="150" style="border-radius: 10px; box-shadow: 0 0 15px #39ff14;">', unsafe_allow_html=True)

st.title("🎟️ Sistema de Gestión Cyberpunk")

# Barra Lateral
st.sidebar.header("⚙️ Configuración del Sistema")
opciones_numeros = [100, 150, 200, 250]
index_defecto = opciones_numeros.index(total_guardado) if total_guardado in opciones_numeros else 0
nuevo_total = st.sidebar.selectbox("¿Capacidad del Servidor (Números)?", opciones_numeros, index=index_defecto)

if nuevo_total != total_guardado:
    df_nueva_config = pd.DataFrame([{"Total": nuevo_total}])
    conn.update(spreadsheet=url_hoja, worksheet="Config", data=df_nueva_config)
    st.rerun()

total_numeros = nuevo_total

# --- PANEL DE CONTROL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Asignar Nuevo Agente")
    with st.form("asignar_form"):
        nombre = st.text_input("ID / Nombre del Agente:")
        disponibles = [n for n in range(1, total_numeros + 1) if n not in compradores]
        
        if disponibles:
            numero = st.selectbox("Selecciona Slot Disponible:", disponibles)
            # Usamos un contenedor para el botón para aplicarle estilos específicos
            st.write("") # Espacio
            submit = st.form_submit_button("REGISTRAR EN LA MATRIZ", type="primary")
            
            if submit:
                if nombre.strip() == "":
                    st.error("⚠️ ERROR: Se requiere identificación del agente.")
                else:
                    nuevo_registro = pd.DataFrame([{"Numero": numero, "Nombre": nombre.strip().title()}])
                    df_ventas_actualizado = pd.concat([df_ventas, nuevo_registro], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_ventas_actualizado)
                    st.success(f"¡REGISTRO EXITOSO! Slot {numero} asignado a {nombre.title()}. Sincronizando...")
                    st.rerun()
        else:
            st.warning("¡SISTEMA LLENO! Todos los slots han sido asignados.")
            st.form_submit_button("REGISTRAR", disabled=True)

with col2:
    st.subheader("🔍 Buscador de Datos")
    busqueda = st.text_input("Escanear por ID o Nombre:")
    
    if busqueda:
        if busqueda.isdigit():
            num_buscado = int(busqueda)
            if num_buscado in compradores:
                dueño = compradores[num_buscado]
                st.success(f"✅ Slot **{num_buscado}** pertenece al agente: **{dueño}**")
            elif num_buscado > total_numeros or num_buscado < 1:
                st.error("⚠️ ERROR: Slot fuera de rango del sistema.")
            else:
                st.info(f"🟢 Slot **{num_buscado}** está LIBRE y listo para asignación.")
        else:
            busqueda_lower = busqueda.lower()
            numeros_encontrados = [num for num, persona in compradores.items() if busqueda_lower in persona.lower()]
            
            if numeros_encontrados:
                numeros_str = ", ".join(map(str, numeros_encontrados))
                st.success(f"👤 Agente **{busqueda.title()}** posee los slots: **{numeros_str}**")
            else:
                st.warning(f"No se encontraron datos para el agente '{busqueda}'.")

# --- ZONA DE BORRADO ---
st.write("---")
with st.expander("🗑️ Protocolo de Liberación de Slot"):
    st.write("ATENCIÓN: Esta acción liberará el slot seleccionado y borrará los datos del agente asociado.")
    if compradores:
        with st.form("borrar_form"):
            numeros_ocupados = sorted(list(compradores.keys()))
            numero_a_borrar = st.selectbox("Selecciona Slot a purgar:", numeros_ocupados)
            submit_borrar = st.form_submit_button("EJECUTAR PURGA")
            if submit_borrar:
                df_ventas['Numero'] = pd.to_numeric(df_ventas['Numero'], errors='coerce')
                df_ventas_actualizado = df_ventas[df_ventas['Numero'] != numero_a_borrar]
                conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_ventas_actualizado)
                st.success(f"✅ Slot {numero_a_borrar} purgado del sistema. Ahora está disponible.")
                st.rerun()
    else:
        st.info("No hay slots ocupados para purgar.")

# --- TABLERO VISUAL (GRID GAMER) ---
st.write("---")
st.subheader("📊 Estado de la Matriz (Grid)")

# CSS específico para el Grid con efectos NEÓN
html_grid = """
<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
        gap: 10px;
        padding: 20px 0;
    }
    .box {
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Rajdhani', sans-serif; /* Aseguramos la fuente en el grid */
        font-weight: 700;
        font-size: 18px;
        color: white;
        padding: 15px 10px;
        border-radius: 4px; /* Bordes más cuadrados estilo tech */
        transition: all 0.3s ease;
        cursor: default;
        border: 1px solid transparent;
    }
    /* ESTILO DISPONIBLE (VERDE RAZER) */
    .disponible {
        background-color: rgba(57, 255, 20, 0.1); /* Fondo verde transparente */
        color: #39ff14;
        border-color: #39ff14;
        box-shadow: 0 0 5px #39ff14; /* Glow suave */
    }
    .disponible:hover {
         background-color: #39ff14;
         color: black;
         box-shadow: 0 0 15px #39ff14, 0 0 30px #39ff14; /* Glow intenso al pasar mouse */
         transform: scale(1.05);
    }

    /* ESTILO OCUPADO (ROJO CYBERPUNK) */
    .ocupado {
        background-color: rgba(255, 57, 57, 0.2); /* Fondo rojo transparente */
        color: #ff3939;
        border-color: #ff3939;
        box-shadow: 0 0 5px #ff3939;
        text-shadow: 0 0 5px #ff3939;
    }
    .ocupado:hover {
         background-color: #ff3939;
         color: white;
         box-shadow: 0 0 20px #ff3939, 0 0 40px #ff3939; /* Glow rojo intenso */
    }
</style>
<div class="grid-container">
"""

for i in range(1, total_numeros + 1):
    if i in compradores:
        nombre_tooltip = compradores[i]
        # Usamos 'data-tooltip' que a veces funciona mejor en Streamlit que 'title'
        html_grid += f'<div class="box ocupado" title="🔴 Slot {i} asignado a: {nombre_tooltip}">{i}</div>'
    else:
        html_grid += f'<div class="box disponible" title="🟢 Slot {i} disponible">{i}</div>'

html_grid += "</div>"
st.markdown(html_grid, unsafe_allow_html=True)
