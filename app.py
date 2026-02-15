import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración principal de la página
st.set_page_config(page_title="Sistema de Rifa", page_icon="🎟️", layout="wide")

# --- CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Tu enlace real de Google Sheets ya está configurado aquí:
url_hoja = "https://docs.google.com/spreadsheets/d/1YcjxsimcbJewI53VVu9exeJxQGmLCP8FkJpFA5OP5cQ/edit?gid=0#gid=0"

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
                    nuevo_registro = pd.DataFrame([{"Numero": numero, "Nombre": nombre.strip().title()}])
                    df_ventas_actualizado = pd.concat([df_ventas, nuevo_registro], ignore_index=True)
                    
                    conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_ventas_actualizado)
                    
                    st.success(f"¡Éxito! Número {numero} guardado permanentemente para {nombre.title()}.")
                    st.rerun()
        else:
            st.warning("¡Todos los números han sido vendidos!")
            st.form_submit_button("Asignar Número", disabled=True)

with col2:
    st.subheader("🔍 Buscador Inteligente")
    busqueda = st.text_input("Ingresa un número o el nombre de una persona:")
    
    if busqueda:
        if busqueda.isdigit():
            num_buscado = int(busqueda)
            if num_buscado in compradores:
                dueño = compradores[num_buscado]
                st.success(f"✅ El número **{num_buscado}** pertenece a: **{dueño}**")
            elif num_buscado > total_numeros or num_buscado < 1:
                st.error("⚠️ Ese número no existe en esta rifa.")
            else:
                st.info(f"🟢 El número **{num_buscado}** está libre y disponible para la venta.")
        else:
            busqueda_lower = busqueda.lower()
            numeros_encontrados = [num for num, persona in compradores.items() if busqueda_lower in persona.lower()]
            
            if numeros_encontrados:
                numeros_str = ", ".join(map(str, numeros_encontrados))
                st.success(f"👤 **{busqueda.title()}** tiene los siguientes números: **{numeros_str}**")
            else:
                st.warning(f"No se encontraron números a nombre de '{busqueda}'.")

# --- NUEVA ZONA: BORRAR / LIBERAR NÚMEROS ---
st.write("---")
with st.expander("🗑️ Corregir / Liberar un número vendido"):
    st.write("Si te equivocaste al asignar un número, puedes borrarlo aquí para que vuelva a estar disponible (en color verde).")
    
    if compradores:
        with st.form("borrar_form"):
            numeros_ocupados = sorted(list(compradores.keys()))
            numero_a_borrar = st.selectbox("Selecciona el número que deseas liberar:", numeros_ocupados)
            
            submit_borrar = st.form_submit_button("Liberar Número")
            
            if submit_borrar:
                # Aseguramos que los números se traten como números para compararlos bien
                df_ventas['Numero'] = pd.to_numeric(df_ventas['Numero'], errors='coerce')
                
                # Filtramos la tabla: Nos quedamos con todos EXCEPTO el número que queremos borrar
                df_ventas_actualizado = df_ventas[df_ventas['Numero'] != numero_a_borrar]
                
                # Truco de Senior: Limpiamos la hoja entera primero para evitar "filas fantasma"
                conn.client.open_by_url(url_hoja).worksheet("Ventas").clear()
                
                # Guardamos la nueva tabla actualizada
                conn.update(spreadsheet=url_hoja, worksheet="Ventas", data=df_ventas_actualizado)
                
                st.success(f"✅ El número {numero_a_borrar} ha sido eliminado y vuelve a estar libre.")
                st.rerun()
    else:
        st.info("Aún no hay números vendidos que puedas borrar.")

# --- TABLERO VISUAL (Grid Dinámico) ---
st.write("---")
st.subheader("📊 Tablero de Disponibilidad")

html_grid = """
<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(55px, 1fr));
        gap: 8px;
        padding: 10px 0;
    }
    .box {
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        padding: 12px;
        border-radius: 6px;
        font-size: 16px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.2);
    }
    .disponible { background-color: #28a745; } /* Verde */
    .ocupado { background-color: #dc3545; }    /* Rojo */
</style>
<div class="grid-container">
"""

for i in range(1, total_numeros + 1):
    if i in compradores:
        nombre_tooltip = compradores[i]
        html_grid += f'<div class="box ocupado" title="Vendido a: {nombre_tooltip}">{i}</div>'
    else:
        html_grid += f'<div class="box disponible" title="Disponible">{i}</div>'

html_grid += "</div>"
st.markdown(html_grid, unsafe_allow_html=True)
