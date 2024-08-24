import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Función para generar o completar la cita usando la API de Together
def generar_cita_completa(titulo, cita_previa):
    api_key = st.secrets["together"]["api_key"]
    endpoint = "https://api.together.xyz/complete"  # Asegúrate de que este es el endpoint correcto
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Preparar el prompt para la API
    if cita_previa:
        prompt = f"Completa la siguiente cita para el título '{titulo}':\n\n{cita_previa}"
    else:
        prompt = f"Genera una cita relevante para el título '{titulo}'."
    
    data = {
        "prompt": prompt,
        "max_tokens": 150  # Ajusta según sea necesario
    }
    
    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP de error
        cita_completa = response.json().get("choices")[0].get("text").strip()
        if cita_completa:
            return cita_completa
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener la cita completa: {e}")
        return None

# Función para buscar citas en Google Scholar
def buscar_citas_en_scholar(tema):
    url = f"https://scholar.google.com/scholar?q={tema.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    resultados = []
    
    # Extraer los resultados
    for entry in soup.select('.gs_ri'):
        titulo_element = entry.select_one('.gs_rt')
        if not titulo_element:
            continue  # Saltar si no hay título
        titulo = titulo_element.get_text()

        referencia_element = entry.select_one('.gs_a')
        referencia = referencia_element.get_text() if referencia_element else "Referencia no disponible"

        cita_previa_element = entry.select_one('.gs_rs')
        cita_previa = cita_previa_element.get_text() if cita_previa_element else None

        # Generar o completar la cita usando la API de Together
        cita_completa = generar_cita_completa(titulo, cita_previa)

        # Solo agregar al resultado si se obtuvo una cita completa
        if cita_completa:
            resultados.append({
                "titulo": titulo,
                "cita": cita_completa,
                "referencia": referencia
            })
        
        # Detenerse si ya se han obtenido 20 resultados con citas disponibles
        if len(resultados) >= 20:
            break
    
    return resultados

# Configuración de la página de Streamlit
st.set_page_config(page_title="Explorador de Citas por Tema", page_icon="🔍")

# Título de la aplicación
st.title("🔍 Explorador de Citas por Tema")

# Formulario de entrada
tema = st.text_input("Ingresa el tema de interés:")

# Botón de búsqueda
if st.button("Buscar"):
    if tema:
        st.write("Buscando citas para el tema:", tema)
        with st.spinner('Procesando...'):
            resultados = buscar_citas_en_scholar(tema)
        
        if resultados:
            st.write(f"Se encontraron {len(resultados)} citas disponibles:")
            for idx, resultado in enumerate(resultados):
                st.subheader(f"Cita {idx + 1}")
                st.write(f"**Título:** {resultado['titulo']}")
                st.write(f"**Cita textual:** {resultado['cita']}")
                st.write(f"**Referencia:** {resultado['referencia']}")
                st.write("---")
        else:
            st.write("No se encontraron citas disponibles para el tema especificado.")
    else:
        st.write("Por favor, ingresa un tema para buscar citas.")
