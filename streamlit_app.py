import streamlit as st
import requests
from bs4 import BeautifulSoup

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
        cita = entry.select_one('.gs_or_ggsm').text if entry.select_one('.gs_or_ggsm') else "No disponible"
        referencia = entry.select_one('.gs_a').text
        resultados.append({
            "titulo": titulo,
            "cita": cita,
            "referencia": referencia
        })
    
    return resultados[:20]

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
