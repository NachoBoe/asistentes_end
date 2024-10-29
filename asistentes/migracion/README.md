# Asistente Experto en Proceso de Migración a Bantotal

## Descripción

Este asistente es un experto en el proceso de migración al software Bantotal, una solución integral para instituciones financieras. Su objetivo es ayudar a los usuarios a comprender y resolver dudas relacionadas con la migración al sistema Bantotal, proporcionando información detallada y precisa sobre los diferentes elementos involucrados en el proceso, como programas de control y vuelco, bandejas, sistemas y transacciones.

El asistente responde a las preguntas de los usuarios en español, utilizando herramientas especializadas para recuperar información relevante y garantizar que todas las respuestas estén fundamentadas en fuentes confiables. Se enfoca en brindar respuestas completas sin ser redundante, y evita proporcionar información fuera del alcance de las consultas o que no esté presente en los textos recuperados.

## Herramientas

El asistente utiliza cuatro herramientas principales para obtener y proporcionar información detallada sobre el proceso de migración:

### 1. retrieve_records_from_description

**Función**: Esta herramienta permite buscar y recuperar registros (campos) basados en una descripción proporcionada sobre el contenido de información que deberían almacenar. Es especialmente útil para identificar campos específicos dentro de las bandejas o tablas relevantes para ciertas operaciones de migración.

**Funcionamiento**:

- **Entrada**: Recibe una descripción del campo que se desea encontrar y, opcionalmente, el sistema al que pertenece (por ejemplo, 'Préstamos', 'Depósitos', etc.).
- **Procesamiento**:
  - Utiliza embeddings generados por el modelo `text-embedding-ada-002` de Azure OpenAI para convertir la descripción en un vector numérico que captura su significado semántico.
  - Realiza una búsqueda vectorial exhaustiva en Azure Cognitive Search para encontrar los campos más relevantes.
  - Filtra los resultados por sistema cuando es posible para mejorar el rendimiento.
- **Salida**: Devuelve una lista de campos adecuados junto con información sobre la bandeja o tabla a la que pertenecen, su descripción y el sistema asociado.

**Desarrollo**:

- Implementada en Python, utilizando las bibliotecas `langchain`, `azure-search-documents` y `azure-openai`.
- Maneja la tokenización y normalización de textos para mejorar la precisión de las búsquedas.
- Ejemplo de código:

  ```python
  class desc_campo(BaseModel):
      description: str = Field(description="Descripción del contenido de información que almacena el registro a encontrar.")
      system: str = Field(description="Sistema para filtrar la búsqueda. Los sistemas posibles son: ['Cuentas Vistas', 'Cuentas y Personas', 'Chequeras', 'Depósitos', 'Microfinanzas', 'Saldos Iniciales', 'Facultades', 'Líneas de Crédito', 'Garantías', 'Préstamos', 'Acuerdos de Sobregiro', 'Tarjetas de Débito', 'Descuentos', 'all']", default="all")

  @tool("retrieve_records_from_description", args_schema=desc_campo)
  def retrieve_records_from_description(description: str, system: str = "all"):
      # Implementación de la función
  ```

### 2. retrieve_sistem_migration_information

**Función**: Recupera información relevante sobre la migración de un sistema específico dentro de Bantotal. Proporciona una visión general de las bandejas, programas de control y vuelco, transacciones, requisitos previos y posibles errores asociados con la migración de ese sistema.

**Funcionamiento**:

- **Entrada**: Nombre del sistema del cual se desea obtener información (por ejemplo, 'Préstamos', 'Depósitos', etc.).
- **Procesamiento**:
  - Accede a los manuales específicos del sistema almacenados localmente.
  - Extrae las secciones más relevantes que describen el proceso de migración para ese sistema, asegurándose de no exceder los límites de tokens permitidos.
- **Salida**: Proporciona contenido detallado que incluye guías conceptuales sobre cómo migrar el sistema, sin enfocarse en cómo ejecutar las operaciones en Bantotal.

**Desarrollo**:

- Implementada en Python, utilizando objetos deserializados con `dill` que contienen los manuales de migración de cada sistema.
- Maneja la tokenización mediante `tiktoken` para controlar el tamaño del contenido retornado.
- Ejemplo de código:

  ```python
  class system_retriever_input(BaseModel):
      system: str = Field(description="Sistema del cual recuperar información. Los sistemas posibles son: ['Cuentas Vistas', 'Cuentas y Personas', ...]")

  @tool("retrieve_sistem_migration_information", args_schema=system_retriever_input)
  def retrieve_sistem_migration_information(system: str):
      # Implementación de la función
  ```

### 3. retrieve_migration_process_information

**Función**: Proporciona información general sobre el proceso de migración a Bantotal, incluyendo una visión general de cómo funciona, una guía detallada sobre cómo ejecutar la migración y detalles sobre los parámetros que personalizan el proceso.

**Funcionamiento**:

- **Entrada**: Indicadores booleanos que especifican qué secciones de información se desean recuperar:
  - `retrieve_sec_1`: Información general del proceso de migración.
  - `retrieve_sec_2`: Guía detallada sobre cómo ejecutar la migración para un sistema.
  - `retrieve_sec_3`: Información detallada sobre los parámetros que personalizan el proceso.
- **Procesamiento**:
  - Extrae las secciones correspondientes del manual general del proceso de migración almacenado localmente.
  - Controla el número de tokens para asegurar que el contenido no exceda los límites establecidos.
- **Salida**: Devuelve el contenido solicitado de manera estructurada.

**Desarrollo**:

- Utiliza técnicas similares a la herramienta anterior para manejar la extracción y tokenización del contenido.
- Ejemplo de código:

  ```python
  class general_retriever_input(BaseModel):
      retrieve_sec_1: bool = Field(description="Recuperar una visión general de cómo funciona el proceso de migración.", default=False)
      retrieve_sec_2: bool = Field(description="Recuperar una guía detallada sobre cómo ejecutar la migración para un sistema.", default=False)
      retrieve_sec_3: bool = Field(description="Recuperar información detallada sobre los parámetros que personalizan el proceso.", default=False)

  @tool("retrieve_migration_process_information", args_schema=general_retriever_input)
  def retrieve_migration_process_information(retrieve_sec_1: bool = False, retrieve_sec_2: bool = False, retrieve_sec_3: bool = False):
      # Implementación de la función
  ```

### 4. retrieve_fields_from_tray

**Función**: Recupera todos los campos (registros) de una bandeja o tabla específica, proporcionando detalles sobre cada campo y su propósito.

**Funcionamiento**:

- **Entrada**:
  - `tray_code`: Código de la bandeja de la cual se desea obtener los campos.
  - `system`: Sistema al que pertenece la bandeja (opcional).
- **Procesamiento**:
  - Busca en los datos locales cargados para encontrar la bandeja especificada.
  - Extrae la información de los campos asociados a esa bandeja.
- **Salida**: Proporciona una descripción detallada de la bandeja, incluyendo su descripción, los registros que contiene y el sistema asociado.

**Desarrollo**:

- Implementada en Python, utilizando datos deserializados con `dill` que contienen información sobre las bandejas y sus campos.
- Maneja casos en los que la bandeja puede pertenecer a varios sistemas o no se encuentra en los datos disponibles.
- Ejemplo de código:

  ```python
  class tray_retriever_input(BaseModel):
      tray_code: str = Field(description="Código de la bandeja de la cual se desean recuperar los campos.")
      system: str = Field(description="Sistema al que pertenece la bandeja. Los sistemas posibles son: ['Cuentas Vistas', 'Cuentas y Personas', ...]", default="all")

  @tool("retrieve_fields_from_tray", args_schema=tray_retriever_input)
  def retrieve_fields_from_tray(tray_code: str, system: str = "all"):
      # Implementación de la función
  ```

**Notas Adicionales**:

- **Uso Transparente de Herramientas**: El asistente utiliza estas herramientas de manera transparente, sin requerir que el usuario conozca su funcionamiento interno.
- **Respuesta Basada en Datos**: Se asegura de que todas las respuestas estén fundamentadas en la información recuperada por las herramientas, evitando conjeturas o información inventada.
- **Optimización de Rendimiento**: Filtra por sistema cuando es posible para mejorar el rendimiento y la relevancia de las búsquedas.

**Tecnologías Utilizadas**:

- **Python**: Lenguaje de programación principal para la implementación.
- **LangChain**: Biblioteca para construir asistentes basados en lenguaje natural.
- **Azure OpenAI Embeddings**: Para generar embeddings semánticos de texto.
- **Azure Cognitive Search**: Servicio para realizar búsquedas vectoriales y semánticas.
- **Dill**: Biblioteca para serializar y deserializar objetos de Python, permitiendo cargar datos locales complejos.
- **tiktoken**: Utilizada para el conteo y manejo de tokens en los textos.

Este conjunto de herramientas permite al asistente proporcionar información precisa y detallada sobre el proceso de migración a Bantotal, ayudando a los usuarios a comprender y navegar por este proceso complejo con mayor facilidad.