# Asistente de Bantotal Campus (BETA)

## Descripción

Este asistente responde a partir de información descrita en los videos de Bantotal Campus. Para esto, se generaron los subtitulos de los videos de los cursos Personas y Descartes. El asistente responde a las preguntas del usuario a partir de la información del video, a la vez que se referencia el video para que el usuario busque más información. El asistente esta en versión BETA porque falta agregar videos de varios cursos.

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
  - Devuelve los resultados que incluyen el texto en la transcripción, el título del video y la URL del video.
  - Organiza los resultados en orden de relevancia, mostrando los 10 más importantes.
