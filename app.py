import streamlit as st
import requests
import json
from typing import List, Dict, Any

# Configuración de la página
st.set_page_config(page_title="Explorador de Citas", page_icon="📚", layout="wide")

# Título y descripción
st.title("Explorador de Citas")
st.markdown("""
    Esta aplicación te ayuda a encontrar citas textuales relevantes de un autor específico sobre un tema en particular.
    Utiliza Serper para buscar en Google Scholar y Together AI para procesar y extraer información relevante.
""")

# Función para hacer la búsqueda en Serper
def search_serper(query: str) -> List[Dict[str, Any]]:
    url = "https://google.serper.dev/scholar"
    payload = json.dumps({"q": query, "num": 20})
    headers = {
        'X-API-KEY': st.secrets["SERPER_API_KEY"],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('organic', [])

# Función para procesar resultados con Together AI
def process_with_together(results: List[Dict[str, Any]], topic: str, author: str) -> List[Dict[str, Any]]:
    prompt = f"""
    Analiza los siguientes resultados de búsqueda para el tema "{topic}" y el autor "{author}".
    Para cada resultado, extrae o genera la siguiente información:
    1. Título del trabajo
    2. Una cita textual relevante (si está disponible, o genera una basada en el resumen)
    3. Autores
    4. Año de publicación
    5. Nombre de la revista o editorial
    6. Volumen e número (si aplica)
    7. Páginas (si aplica)
    8. DOI (si está disponible)

    Resultados:
    {json.dumps(results, indent=2)}

    Proporciona la información en formato JSON.
    """

    response = requests.post(
        "https://api.together.xyz/inference",
        headers={
            "Authorization": f"Bearer {st.secrets['TOGETHER_API_KEY']}",
            "Content-Type": "application/json"
        },
        json={
            "model": "togethercomputer/llama-2-70b-chat",
            "prompt": prompt,
            "max_tokens": 2000,
            "temperature": 0.7
        }
    )
    return json.loads(response.json()['output'])

# Interfaz de usuario
topic = st.text_input("Tema:", placeholder="Ej: Inteligencia Artificial")
author = st.text_input("Autor:", placeholder="Ej: Alan Turing")

if st.button("Buscar Citas"):
    if topic and author:
        with st.spinner('Buscando citas...'):
            # Realizar búsqueda
            query = f"{topic} author:\"{author}\""
            search_results = search_serper(query)
            
            # Procesar resultados
            processed_results = process_with_together(search_results, topic, author)

            # Mostrar resultados
            st.subheader(f"Resultados de la búsqueda para \"{topic}\" de {author}")
            
            for i, citation in enumerate(processed_results, 1):
                with st.expander(f"{i}. {citation['title']}"):
                    st.markdown(f"**Cita textual:** _{citation['excerpt']}_")
                    st.markdown(f"""
                    **Referencia:**
                    {citation['authors']}. ({citation['year']}). {citation['title']}. 
                    *{citation.get('journal', 'Fuente no especificada')}*
                    {f", {citation['volume']}" if 'volume' in citation else ''}
                    {f"({citation['issue']})" if 'issue' in citation else ''}
                    {f": {citation['pages']}" if 'pages' in citation else ''}.
                    {f"DOI: {citation['doi']}" if 'doi' in citation else ''}
                    """)
    else:
        st.warning("Por favor, ingrese tanto el tema como el autor para realizar la búsqueda.")

# Explicación adicional
st.markdown("""
---
### ¿Cómo funciona esta aplicación?

1. Ingresas un tema de interés y el nombre de un autor en el formulario.
2. La aplicación utiliza la API de Serper para buscar en Google Scholar citas relacionadas con el tema, escritas por el autor especificado.
3. Los resultados de la búsqueda se procesan utilizando la API de Together AI para extraer y estructurar la información relevante.
4. Se muestran hasta 20 resultados, cada uno con el título del trabajo, una cita textual relevante (si está disponible) y la referencia bibliográfica completa.

Esta herramienta es ideal para investigadores, estudiantes o cualquier persona interesada en explorar el pensamiento de un autor sobre un tema específico.
""")

# Nota sobre el uso de APIs
st.sidebar.markdown("""
### Nota sobre el uso de APIs

Esta aplicación utiliza las siguientes APIs:
- Serper API para realizar búsquedas en Google Scholar
- Together AI API para procesar y estructurar los resultados

Las claves API están almacenadas de forma segura en los secrets de Streamlit y no son accesibles públicamente.
""")
