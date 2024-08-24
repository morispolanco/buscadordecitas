import streamlit as st
import requests
import json
from typing import List, Dict, Any

# ... [El resto del código anterior permanece igual] ...

# Función actualizada para procesar resultados con Together AI
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

    try:
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
        response.raise_for_status()  # Esto lanzará una excepción para códigos de estado HTTP no exitosos
        
        response_json = response.json()
        if 'output' not in response_json:
            st.error(f"La respuesta de Together AI no contiene el campo 'output'. Respuesta completa: {response_json}")
            return []

        try:
            return json.loads(response_json['output'])
        except json.JSONDecodeError:
            st.error(f"No se pudo decodificar la salida JSON de Together AI. Salida: {response_json['output']}")
            return []

    except requests.RequestException as e:
        st.error(f"Error al hacer la solicitud a Together AI: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error inesperado al procesar con Together AI: {str(e)}")
        return []

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

            if not processed_results:
                st.warning("No se pudieron procesar los resultados. Por favor, intente de nuevo.")
            else:
                # Mostrar resultados
                st.subheader(f"Resultados de la búsqueda para \"{topic}\" de {author}")
                
                for i, citation in enumerate(processed_results, 1):
                    with st.expander(f"{i}. {citation.get('title', 'Título no disponible')}"):
                        st.markdown(f"**Cita textual:** _{citation.get('excerpt', 'No disponible')}_")
                        st.markdown(f"""
                        **Referencia:**
                        {citation.get('authors', 'Autores no especificados')}. ({citation.get('year', 'Año no especificado')}). {citation.get('title', 'Título no disponible')}. 
                        *{citation.get('journal', 'Fuente no especificada')}*
                        {f", {citation['volume']}" if 'volume' in citation else ''}
                        {f"({citation['issue']})" if 'issue' in citation else ''}
                        {f": {citation['pages']}" if 'pages' in citation else ''}.
                        {f"DOI: {citation['doi']}" if 'doi' in citation else ''}
                        """)
    else:
        st.warning("Por favor, ingrese tanto el tema como el autor para realizar la búsqueda.")

# ... [El resto del código permanece igual] ...
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
