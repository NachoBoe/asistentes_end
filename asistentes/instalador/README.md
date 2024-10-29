# Asistente Experto en Proceso de Instalación de Bantotal

## Descripción

Este asistente es un experto en el proceso de instalación de Bantotal, un software especializado que proporciona soluciones para instituciones financieras. Bantotal ofrece numerosos sistemas, cada uno orientado a satisfacer diferentes necesidades, y es accesible a través de pantallas altamente parametrizables.

El asistente está diseñado para ayudar al equipo de instalación brindando la información necesaria para instalar el software de manera eficiente. Utiliza un motor de búsqueda que recupera información relevante del sistema Bantotal, incluyendo detalles sobre pantallas, parametrizaciones y otros aspectos críticos del proceso de instalación.

Las respuestas del asistente se proporcionan en español, asegurando que toda la información esté fundamentada en el contexto recuperado y nunca inventada. Además, siempre referencia la fuente de la información, indicando la sección y el manual de donde se obtuvo, y presenta la información de forma clara y concisa para facilitar su comprensión.

## Herramientas

### system_informaton

Esta herramienta es un motor de búsqueda semántico que permite al asistente recuperar información relevante del sistema Bantotal, específicamente enfocada en el proceso de instalación. Es fundamental para proporcionar respuestas precisas y basadas en fuentes confiables.

**Funcionamiento**:

- **Entrada**: Recibe una consulta (`query`) que representa la pregunta o necesidad de información del usuario.
- **Procesamiento**:
  - Utiliza el modelo de embeddings `text-embedding-3-large` de Azure OpenAI para convertir la consulta en un vector numérico que captura su significado semántico.
  - Realiza una búsqueda vectorial y semántica en el índice `instalador` de Azure Search, buscando en el campo `embedding`.
  - Configura la búsqueda para obtener los 5 resultados más relevantes, aplicando una búsqueda exhaustiva y evitando resultados duplicados o solapados.
- **Salida**:
  - Devuelve una respuesta estructurada que incluye:
    - **Manual**: Nombre del manual de instalación (MDI) y el sistema correspondiente, formateado en mayúsculas.
    - **Sección**: Ruta específica dentro del manual de donde se extrajo la información.
    - **Contenido**: El contenido relevante encontrado en esa sección.

**Desarrollo**:

La herramienta está implementada en Python y utiliza varias bibliotecas y servicios clave:

- **Azure OpenAI Embeddings**: Para generar representaciones numéricas (embeddings) de las consultas, capturando su significado semántico.
- **Azure Search**: Para realizar búsquedas avanzadas y semánticas en la base de datos de Bantotal, aprovechando la capacidad de manejo de grandes volúmenes de información.
- **LangChain**: Para estructurar la herramienta y facilitar su integración en el flujo de trabajo del asistente.
- **Funciones Auxiliares**: Como `remover_tildes`, que normaliza las cadenas de texto para mejorar la eficacia en la búsqueda.

El código de la herramienta es el siguiente:

```python
# Importaciones necesarias
import os
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
import unicodedata
from azure.search.documents.models import VectorizedQuery, QueryType, QueryCaptionType, QueryAnswerType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_openai import AzureOpenAIEmbeddings

# Configuración de embeddings y cliente de búsqueda
embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large")
index_name = "instalador"
credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_API_KEY"])
endpoint = "https://bantotalsearchai.search.windows.net"
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

# Función auxiliar para remover tildes
def remover_tildes(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')

# Definición del esquema de entrada
class Query(BaseModel):
    query: str = Field(description="Consulta para buscar en el motor.")

# Implementación de la herramienta
@tool("system_informaton", args_schema=Query)
def system_informaton(query: str):
    """Motor de búsqueda semántico de Bantotal que recupera información relevante del sistema."""
    embedding = embeddings.embed_query(query)
    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=50,
        fields="embedding",
        exhaustive=True
    )
    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["id", "content", "section", "path", "system"],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='my-semantic-config',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=5,
    )

    ans = ""
    results_record = []
    for result in results:
        print(result["path"] + " - " + str(result["@search.reranker_score"]))
        results_record.append(result)
    
    retrieved_sections = [x["section"] for x in results_record]
    
    for result in results_record:
        sec = result["section"]
        if not any([sec.startswith(x) and x != sec for x in retrieved_sections]):
            ans += f"Manual: MDI - {(result['system']).replace('_', '').upper()} \n"
            ans += f"Sección: {result['path']} \n"
            ans += f"Contenido: \n{result['content']} \n"
            ans += "\n\n"
    return ans
```

**Características clave**:

- **Búsqueda Semántica Avanzada**: Utiliza embeddings para comprender el significado de las consultas y recuperar información altamente relevante.
- **Referencia de Fuentes**: Cumple con la instrucción de siempre referenciar la fuente, indicando el manual y la sección exacta de donde se obtuvo la información.
- **Eficiencia en la Recuperación de Información**: Implementa lógica para evitar información duplicada o redundante, asegurando que las respuestas sean precisas y útiles.
- **Integración Sencilla**: Gracias a LangChain y a una estructura de código clara, la herramienta se integra perfectamente en el asistente, facilitando su mantenimiento y actualización.

Esta herramienta es esencial para que el asistente pueda proporcionar al equipo de instalación información precisa y confiable, directamente extraída de los manuales oficiales de Bantotal, asegurando así un proceso de instalación más eficiente y efectivo.