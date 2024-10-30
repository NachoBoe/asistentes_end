# Asistente Experto en Documentación de la API de Bantotal

## Descripción

Este asistente es un experto en la documentación de la API de Bantotal Services. El asistente utiliza herramientas especializadas para buscar y proporcionar información precisa basada en las consultas del usuario.


## Herramientas

### get_methods_from_description

Esta herramienta devuelve una lista de posibles métodos de la API basado en una descripción de lo que se quiere hacer.  Devuelve el nombre de los métodos, el sistema al que pertenece cada uno y una breve descripción de estos.

**Funcionamiento**:

- **Entrada**: Recibe una descripción del método que el usuario necesita.
- **Procesamiento**:
  - Utiliza embeddings proporcionados por `AzureOpenAIEmbeddings` para convertir la descripción en un vector numérico.
  - Realiza una búsqueda vectorial y semántica en el índice `api_final` de Azure Cognitive Search para encontrar métodos relevantes.
  - Recupera hasta 15 métodos que coinciden con la descripción.
- **Salida**:
  - Devuelve una lista de métodos con su nombre, sistema y descripción breve.

### get_method_info_from_name

Esta herramienta proporciona información detallada sobre un método específico, incluyendo su esquema de entrada y salida, posibles errores y ejemplos de llamadas utilizando SOAP o JSON.

**Funcionamiento**:

- **Entrada**: Recibe el nombre del método y el sistema al que pertenece.
- **Procesamiento**:
  - Construye un filtro para buscar exactamente el método y sistema especificados.
  - Realiza una búsqueda semántica en el índice `api_final` para recuperar la información detallada del método.
- **Salida**:
  - Devuelve información detallada del método, incluyendo su descripción, entrada, salida, errores y ejemplos.

