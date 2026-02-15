import streamlit as st
import pandas as pd

# 1. Configuración principal de la página
st.set_page_config(page_title="Sistema de Rifa", page_icon="🎟️", layout="wide")

# --- BASE DE DATOS TEMPORAL (En memoria) ---
# Aquí guardamos quién compró qué. Formato: {numero_boleto: "Nombre Persona"}
if "compradores" not in st.session_state:
    st.session_state.compradores = {} 

st.title("🎟️ Sistema de Gestión de Rifas")

# --- 2. BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuración")
opciones_numeros = [100, 150, 200, 250]
total_numeros = st.sidebar.selectbox("¿De cuántos números es la rifa?", opciones_numeros)

# --- 3. PANEL DE CONTROL (Asignar y Buscar) ---
# Usamos columnas para que se vea profesional y organizado
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Vender / Asignar Número")
    # Usamos un formulario para evitar que la página se recargue mientras escribes
    with st.form("asignar_form"):
        nombre = st.text_input("Nombre de la persona:")
        
        # Generar lista de números que AÚN NO están en el diccionario de compradores
        disponibles = [n for n in range(1, total_numeros + 1) if n not in st.session_state.compradores]
        
        if disponibles:
            numero = st.selectbox("Selecciona un número disponible:", disponibles)
            submit = st.form_submit_button("Asignar Número", type="primary")
            
            if submit:
                if nombre.strip() == "":
                    st.error("⚠️ Debes ingresar un nombre.")
                else:
                    # Guardamos el número y el nombre
                    st.session_state.compradores[numero] = nombre.strip().title()
                    st.success(f"¡Éxito! Número {numero} asignado a {nombre.title()}.")
                    st.rerun() # Refresca para actualizar el tablero
        else:
            st.warning("¡Felicidades, todos los números han sido vendidos!")
            st.form_submit_button("Asignar Número", disabled=True)

with col2:
    st.subheader("🔍 Buscador Inteligente")
    busqueda = st.text_input("Ingresa un número o el nombre de una persona:")
    
    if busqueda:
        # LÓGICA 1: Si lo que escribió el usuario es un número
        if busqueda.isdigit():
            num_buscado = int(busqueda)
            if num_buscado in st.session_state.compradores:
                dueño = st.session_state.compradores[num_buscado]
                st.success(f"✅ El número **{num_buscado}** pertenece a: **{dueño}**")
            elif num_buscado > total_numeros or num_buscado < 1:
                st.error("⚠️ Ese número no existe en esta rifa.")
            else:
                st.info(f"🟢 El número **{num_buscado}** está libre y disponible para la venta.")
        
        # LÓGICA 2: Si lo que escribió es texto (Búsqueda por nombre)
        else:
            busqueda_lower = busqueda.lower()
            # Buscamos en el diccionario todos los números que coincidan con el nombre
            numeros_encontrados = [num for num, persona in st.session_state.compradores.items() if busqueda_lower in persona.lower()]
            
            if numeros_encontrados:
                # Convertimos la lista de números a texto separado por comas
                numeros_str = ", ".join(map(str, numeros_encontrados))
                st.success(f"👤 **{busqueda.title()}** tiene los siguientes números: **{numeros_str}**")
            else:
                st.warning(f"No se encontraron números a nombre de '{busqueda}'.")

# --- 4. TABLERO VISUAL (Grid Dinámico) ---
st.write("---")
st.subheader("📊 Tablero de Disponibilidad")
st.caption("Los recuadros en verde están libres. Los rojos están vendidos (pasa el ratón sobre ellos para ver el dueño).")

# Usamos HTML y CSS puro para renderizar 250 recuadros de forma súper rápida
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
    .disponible { background-color: #28a745; } /* Verde Streamlit */
    .ocupado { background-color: #dc3545; }    /* Rojo */
</style>
<div class="grid-container">
"""

# Bucle para crear cada recuadro del 1 al total seleccionado
for i in range(1, total_numeros + 1):
    if i in st.session_state.compradores:
        nombre_tooltip = st.session_state.compradores[i]
        # Agregamos la clase 'ocupado' (rojo) y un 'title' para que al pasar el mouse salga el nombre
        html_grid += f'<div class="box ocupado" title="Vendido a: {nombre_tooltip}">{i}</div>'
    else:
        # Agregamos la clase 'disponible' (verde)
        html_grid += f'<div class="box disponible" title="Disponible">{i}</div>'

html_grid += "</div>"

# Le decimos a Streamlit que dibuje nuestro código HTML
st.markdown(html_grid, unsafe_allow_html=True)
