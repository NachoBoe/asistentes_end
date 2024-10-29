# Asistente Experto en Bantotal

## Descripción

Este asistente es un experto en Bantotal, una empresa que proporciona software para instituciones financieras. Su propósito es ayudar al usuario con cualquier pregunta que tenga sobre el sistema Bantotal. Para ello, el asistente tiene acceso a un motor de búsqueda que recupera información relevante directamente de Bantotal.

El asistente sigue estrictamente las siguientes instrucciones:

1. **Respuesta en Español**: Todas las respuestas se proporcionan en español.
2. **Información Detallada y Relevante**: Ofrece información detallada pero siempre enfocada en la pregunta del usuario.
3. **Información Basada en Contexto**: Nunca inventa información. Toda la información se basa en el contexto recuperado por el motor de búsqueda. Si el motor no proporciona la información necesaria, el asistente informa al usuario que no dispone de esa información.
4. **Manejo de Imágenes**: Las imágenes en la fuente original se reemplazan por descripciones encerradas entre etiquetas `<image>`.
5. **Referencia de Fuentes**: Siempre referencia la fuente de la información proporcionada, incluyendo el nombre del manual y la sección correspondiente.
6. **Referencia a Pantallas**: Al ayudar al usuario a navegar por el sistema, puede referenciar el código de la pantalla, ya que el usuario comprende esta referencia.

## Herramientas

### bantotal_informaton

Esta herramienta es un motor de búsqueda semántico que recupera información relevante del sistema Bantotal. Es fundamental para que el asistente proporcione respuestas precisas y fundamentadas en fuentes oficiales.

**Funcionamiento**:

- **Entrada**:
  - Recibe una consulta (`query`) formulada por el usuario.
- **Procesamiento**:
  - Utiliza el modelo de embeddings `text-embedding-3-large` de Azure OpenAI para convertir la consulta en un vector numérico.
  - Realiza una búsqueda vectorial y semántica en el índice `mdu` de Azure Search, buscando en el campo `embedding`.
  - Configura la búsqueda para obtener los 5 resultados más relevantes, utilizando configuraciones semánticas avanzadas para mejorar la pertinencia de los resultados.
  - Filtra los resultados para evitar duplicados y asegurar que la información sea única y relevante.
- **Salida**:
  - Devuelve una respuesta estructurada que incluye:
    - **Manual**: Nombre del manual de usuario de Bantotal de donde se obtuvo la información.
    - **Sección**: Ruta o sección específica dentro del manual.
    - **Contenido**: El contenido relevante extraído del manual.

**Desarrollo**:

La herramienta está implementada utilizando varias tecnologías y bibliotecas:

- **Azure OpenAI Embeddings**: Para convertir las consultas en embeddings numéricos que capturan el significado semántico.
- **Azure Search**: Para realizar búsquedas avanzadas y semánticas en el índice de documentos de Bantotal.
- **LangChain**: Para estructurar y facilitar la integración de la herramienta en el asistente.
- **Python**: Lenguaje de programación utilizado para implementar la lógica de la herramienta.

**Código de la Herramienta**:

```python
import os
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
import unicodedata
from azure.search.documents.models import VectorizedQuery, QueryType, QueryCaptionType, QueryAnswerType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_openai import AzureOpenAIEmbeddings

# Configuración de Azure AI Search
embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large")
index_name = "mdu"
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
@tool("bantotal_informaton", args_schema=Query)
def bantotal_informaton(query: str):
    """Motor de búsqueda semántico de Bantotal que recupera información relevante."""

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
        
    for result in results_record:
        sec = result["section"]
        sys = result["system"]
        if not any(
            (sec.startswith(x["section"]) and x["section"] != sec and sys == x["system"])
            for x in results_record
        ):
            ans += f"Manual: 'MDU-{result['system'].replace('_', ' ').upper()}' \n"
            ans += f"Sección: {result['path']} \n"
            ans += f"Contenido: \n{result['content']} \n"
            ans += "\n\n"
    return ans
```

**Características Clave**:

- **Búsqueda Semántica Avanzada**: Aprovecha el poder de los embeddings y la búsqueda semántica para entender el contexto de las consultas y proporcionar resultados precisos.
- **Referencias Claras**: Siempre indica el manual y la sección de donde se obtuvo la información, facilitando al usuario la verificación y ampliación de la información.
- **Filtrado Eficiente**: Implementa lógica para evitar resultados duplicados y asegurar que la información sea relevante y no redundante.
- **Integración Transparente**: La herramienta está diseñada para integrarse perfectamente con el asistente, permitiéndole ofrecer respuestas fundamentadas y útiles.

**Uso en el Asistente**:

Esta herramienta es esencial para que el asistente cumpla con su tarea de ayudar al usuario con preguntas sobre el sistema Bantotal, asegurando que todas las respuestas estén basadas en información oficial y actualizada, y que sean proporcionadas de manera clara y concisa.