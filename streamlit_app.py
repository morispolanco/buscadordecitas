import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

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
        titulo = entry.select_one('.gs_rt').text
        referencia = entry.select_one('.gs_a').text
        cita_previa = entry.select_one('.gs_rs').text if entry.select_one('.gs_rs') else None
        
        # Si no hay cita previa, generar una cita relevante
        cita_completa = generar_cita_completa(titulo, cita_previa)
        
        resultados.append({
            "titulo": titulo,
            "cita": cita_completa,
            "referencia": referencia
        })
    
    return resultados[:20]

# Función para generar o completar la cita usando la API de Together
def generar_cita_completa(titulo, cita_previa):
    api_key = st.secrets["together"]["api_key"]
    endpoint = "https://api.together.xyz/complete"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Preparamos la solicitud para la API
    prompt = f"Complete the following citation for the title '{titulo}':\n\n{cita_previa}" if cita_previa else f"Generate a relevant citation for the title '{titulo}'."
    
    data = {
        "prompt": prompt,
        "max_tokens": 100
    }
    
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        cita_completa = response.json().get("choices")[0]["text"].strip()
        return cita_completa
    else:
        return "Cita no disponible"

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
        resultados = buscar_citas_en_scholar(tema)
        
        if resultados:
            st.write(f"Se encontraron {len(resultados)} citas:")
            for idx, resultado in enumerate(resultados):
                st.subheader(f"Cita {idx + 1}")
                st.write(f"**Título:** {resultado['titulo']}")
                st.write(f"**Cita textual:** {resultado['cita']}")
                st.write(f"**Referencia:** {resultado['referencia']}")
                st.write("---")
        else:
            st.write("No se encontraron citas para el tema especificado.")
    else:
        st.write("Por favor, ingresa un tema para buscar citas.")
