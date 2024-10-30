# Asistente Experto en Proceso de Migración a Bantotal

## Descripción

Este asistente es un experto en el proceso de migración a Bantotal. Su objetivo es ayudar a los usuarios a comprender y resolver dudas relacionadas con la migración al sistema Bantotal, proporcionando información detallada y precisa sobre los diferentes elementos involucrados en el proceso, como programas de control y vuelco, bandejas, sistemas y transacciones.


## Herramientas

El asistente utiliza cuatro herramientas principales para obtener y proporcionar información detallada sobre el proceso de migración:

### 1. retrieve_records_from_description

**Función**: Esta herramienta permite buscar y recuperar registros (campos) de diferentes bandejas a partir de una descripción proporcionada sobre el contenido de información que deberían almacenar. Es especialmente útil para identificar en que campos dentro de las bandejas se guarda cierta información.

**Funcionamiento**:

- **Entrada**: Recibe una descripción de la información que se desea encontrar en que campo guardar y, opcionalmente, el sistema al que pertenece.

- **Procesamiento**:
  - Utiliza embeddings generados por el modelo `text-embedding-ada-002` de Azure OpenAI para convertir la descripción en un vector numérico que captura su significado semántico.
  - Realiza una búsqueda vectorial exhaustiva en Azure Cognitive Search para encontrar los campos más relevantes.
  - Filtra los resultados por sistema cuando es posible para mejorar el rendimiento.
- **Salida**: Devuelve una lista de campos adecuados junto con información sobre la bandeja o tabla a la que pertenecen, su descripción y el sistema asociado.


### 2. retrieve_sistem_migration_information

**Función**: Recupera información relevante sobre la migración de un sistema específico dentro de Bantotal. Proporciona una visión general de las bandejas, programas de control y vuelco, transacciones, requisitos previos y posibles errores asociados con la migración de ese sistema.

**Funcionamiento**:

- **Entrada**: Nombre del sistema del cual se desea obtener información (por ejemplo, 'Préstamos', 'Depósitos', etc.).
- **Procesamiento**:
  - Accede a los manuales específicos del sistema almacenados localmente.
  - Extrae las secciones más relevantes que describen el proceso de migración para ese sistema, asegurándose de no exceder los límites de tokens permitidos.
- **Salida**: Proporciona contenido detallado que incluye guías conceptuales sobre cómo migrar el sistema, sin enfocarse en cómo ejecutar las operaciones en Bantotal.

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
