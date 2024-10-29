# Asistente Experto en Bantotal

## Descripción

Este asistente es un experto en Bantotal y está diseñado para ayudar a los usuarios respondiendo a sus preguntas en español. Todas las respuestas proporcionadas por el asistente se basan exclusivamente en información recuperada mediante el motor de búsqueda proporcionado como herramienta. Este motor de búsqueda está construido a partir de transcripciones de videos tutoriales sobre cómo usar Bantotal. Cada vez que el asistente proporciona una respuesta, siempre referencia la URL del video correspondiente, permitiendo al usuario acceder directamente al material original para obtener más información. El asistente se esfuerza por ser conciso en sus respuestas y siempre incluye el enlace al video relevante para mayor claridad.

## Herramientas

### bantotal_search_engine

Esta herramienta es un motor de búsqueda que permite al asistente encontrar información relevante a las preguntas del usuario en una base de datos compuesta por transcripciones de videos tutoriales de Bantotal. Devuelve los 10 resultados más relevantes en orden de importancia.

**Funcionamiento**:

- **Entrada**: Recibe una pregunta formulada por el usuario.
- **Procesamiento**:
  - Utiliza el modelo de embeddings `text-embedding-3-small` de Azure OpenAI para convertir la pregunta en un vector numérico.
  - Realiza una búsqueda vectorial en la base de datos utilizando `VectorizedQuery`, buscando en el campo `texto_vector`.
  - Configura la búsqueda para ser de tipo semántico, permitiendo obtener resultados más relevantes contextualmente.
- **Salida**:
  - Devuelve los resultados que incluyen el texto relevante, el título del video y la URL del video.
  - Organiza los resultados en orden de relevancia, mostrando los 10 más importantes.

**Desarrollo**:

La herramienta está implementada utilizando varias bibliotecas y servicios clave:

- **Azure OpenAI Embeddings**: Para generar embeddings de las preguntas del usuario.
- **Azure Search Client**: Para realizar búsquedas semánticas y vectoriales en la base de datos de transcripciones.
- **LangChain**: Para estructurar y facilitar la integración de la herramienta en el asistente.

El código de la herramienta es el siguiente:

```python
@tool("bantotal_search_engine", args_schema=query_search_engine)
def bantotal_search_engine(question: str):
    """Busca información relevante a la pregunta en la base de datos. Devuelve los 10 mejores resultados en orden de relevancia."""
    embedding = embeddings.embed_query(question)
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=30, fields="texto_vector")

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        select=["id", "text", "titulo", "url", "inicio", "fin", "idx", "texto_vector"],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='my-semantic-config',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=10,
    )

    answer = ""

    for result in results:
        answer += f"texto: {result['text']}\n"
        answer += f"Video: {result['titulo']}\n"
        answer += f"url: {result['url']}\n\n"
    return answer
```

Esta función utiliza el decorador `@tool` de LangChain para definir una herramienta que puede ser llamada por el asistente. La clase `query_search_engine` define el esquema de entrada, asegurando que la pregunta del usuario se procese correctamente.

**Características clave**:

- **Búsqueda Semántica**: Permite entender el contexto y significado de la pregunta del usuario, ofreciendo resultados más precisos.
- **Referencias a Videos**: Siempre incluye la URL del video de donde se extrajo la información, facilitando al usuario el acceso a recursos adicionales.
- **Respuesta Concisa**: Organiza y presenta la información de manera clara y directa.

Esta herramienta es fundamental para que el asistente proporcione respuestas precisas y útiles, siempre respaldadas por material oficial y referenciando las fuentes originales.