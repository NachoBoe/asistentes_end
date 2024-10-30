# Asistente Experto en Bantotal Core Instalador (BETA)

## Descripción

Este asistente es un experto en el proceso de instalación de los diferentes módulos de Bantotal Core.

## Herramientas

### system_informaton

Esta herramienta es un motor de búsqueda semántico sobre un indice alimentado de los MDI (Manuales de Instalación) de los indices de Bantotal Core

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
