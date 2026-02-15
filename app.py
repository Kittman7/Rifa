import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración principal de la página
st.set_page_config(page_title="Sistema de Rifa", page_icon="🎟️", layout="wide")

# --- CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 👇 AQUÍ ESTÁ LA CORRECCIÓN. Pega aquí el enlace de tu navegador, NO el correo de la cuenta de servicio.
url_hoja = "https://docs.google.com/spreadsheets/d/https://docs.google.com/spreadsheets/d/1YcjxsimcbJewI53VVu9exeJxQGmLCP8FkJpFA5OP5cQ/edit?gid=0#gid=0" 

# --- LEER DATOS GUARDADOS ---
# Intentamos leer la pestaña Ventas
try:
    df_ventas = conn.read(spreadsheet=url_hoja, worksheet="Ventas", ttl=0)
    df_ventas = df_ventas.dropna(how="all") # Limpiamos filas vacías
except Exception:
    df_ventas = pd.DataFrame(columns=["Numero", "Nombre"])

# Intentamos leer la pestaña Config para saber cuántos números cargar por defecto
try:
    df_config = conn.read(spreadsheet=url_hoja, worksheet="Config", ttl=0)
    df_config = df_config.dropna(how="all")
    total_guardado = int(df_config.iloc[0]["Total"]) if not df_config.empty else 150
except Exception:
    total_guardado = 150

# --- PROCESAR LOS DATOS PARA LA APLICACIÓN ---
# Convertimos el Excel a un diccionario súper rápido para buscar {numero: nombre}
compradores = {}
if not df_ventas.empty and "Numero" in df_ventas.columns:
    for index, row in df_ventas.dropna(subset=["Numero", "Nombre"]).iterrows():
        compradores[int(row["Numero"])] = str(row["Nombre"]).title()

# --- INTERFAZ VISUAL ---
st.title("🎟️ Sistema de Gestión de Rifas")

# Barra Lateral: Configuración Permanente
st.sidebar.header("⚙️ Configuración")
opciones_numeros = [100, 150, 200, 250]

# Seleccionamos por defecto el que está guardado en Google Sheets
index_defecto = opciones_numeros.index(total_guardado) if total_guardado in opciones_numeros else 0
nuevo_total = st.sidebar.selectbox("¿De cuántos números es la rifa?", opciones_numeros, index=index_defecto)

# Si cambiaste el número en el menú, lo guardamos para siempre en Google Sheets
if nuevo_total != total_guardado:
    df_nueva_config = pd.DataFrame([{"Total": nuevo_total}])
    conn.update(spreadsheet=url_hoja, worksheet="Config", data=df_nueva_config)
    st.rerun()

total_numeros = nuevo_total

# --- PANEL DE CONTROL (Asignar y Buscar) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Vender / Asignar Número")
    with st.form("asignar_form"):
        nombre = st.text_input("Nombre de la persona:")
        disponibles = [n for n in range(1, total_numeros + 1) if n not in compradores]
        
        if disponibles:
            numero = st.selectbox("Selecciona un número disponible:", disponibles)
            submit = st.form_submit_button("Guardar en Base de Datos", type="primary")
            
            if submit:
                if nombre.strip() == "":
                    st.error("⚠️ Debes ingresar un nombre.")
                else:
                    # 1. Agregamos el nuevo registro al DataFrame
                    nuevo_registro = pd.DataFrame([{"Numero": numero, "Nombre": nombre.strip().title()}])
                    df_ventas_actualizado = pd.concat([df_ventas, nuevo_registro], ignore_index=True)
                    
                    # 2. GUARDAMOS EN GOOGLE SHEETS PARA SIEMPRE
                    conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_ventas_actualizado)
                    
                    st.success(f"¡Éxito! Número {numero} guardado permanentemente para {nombre.title()}.")
                    st.rerun() # Refresca para pintar el cuadro rojo
        else:
            st.warning("¡Todos los números han sido vendidos!")
            st.form_submit_button("Asignar Número",
