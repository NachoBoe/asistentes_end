# Asistente Experto en Bantotal Core Usuarios (BETA)

## Descripción

Este asistente es un experto en el para usuarios de los módulos de Bantotal Core. El asistente recupera su información a partir de los MDU (Manuales de Usuario) de los distintos módulos.


## Herramientas

### bantotal_informaton

Esta herramienta es un motor de búsqueda semántico que recupera información relevante de los MDU de los modulos de Bantotal Core.

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
