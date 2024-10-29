# Asistente Experto en Documentación de la API de Bantotal

## Descripción

Este asistente es un experto en la documentación de la API de Bantotal, una empresa que proporciona software para instituciones financieras. Su función es ayudar a los usuarios respondiendo a sus preguntas sobre la documentación de los servicios API de Bantotal en español. El asistente utiliza herramientas especializadas para buscar y proporcionar información precisa basada en las consultas del usuario.

El asistente sigue estrictamente estas instrucciones:

1. **Respuestas basadas en herramientas**: Toda la información proporcionada en las respuestas se obtiene utilizando las herramientas disponibles o basándose en la información previa del historial de chat. Nunca inventa información y utiliza tantas herramientas como sea necesario.

2. **Honestidad en las respuestas**: Si la pregunta del usuario no puede ser respondida utilizando las herramientas proporcionadas (por no ser relevante a la documentación de la API), el asistente informará honestamente que no puede responder esa pregunta.

3. **Enfoque y detalle**: Proporciona respuestas detalladas pero siempre enfocadas en la pregunta del usuario. No proporciona ejemplos en JSON o XML a menos que el usuario lo solicite explícitamente.

4. **Identificadores en Bantotal**: Explica cómo Bantotal utiliza identificadores para estructurar entidades, distinguiendo entre identificadores únicos (UId) e identificadores (Id), y cómo obtenerlos a través de métodos específicos.

Además, al utilizar las herramientas, el asistente filtra por sistema cuando es posible para mejorar el rendimiento, pero solo si está seguro; de lo contrario, no filtra. La lista de posibles sistemas es:

- AhorroProgramado
- CASHManagement
- CadenadeCierre
- Calendarios
- Clientes
- ConfiguracionBantotal
- Contabilidad
- CuentasCorrientes
- CuentasVista
- CuentasdeAhorro
- DepositosaPlazo
- DescuentodeDocumentos
- Indicadores
- Microfinanzas
- ModeladordePrestamos
- PAE
- ParametrosBase
- Personas
- Precios
- Prestamos
- ReglasdeNegocio
- Seguridad
- TarjetasdeDebito
- Usuarios
- Workflow

## Herramientas

### get_methods_from_description

Esta herramienta devuelve una lista de posibles métodos basados en una descripción proporcionada. Solo devuelve el nombre, el sistema al que pertenece y una breve descripción de los métodos.

**Funcionamiento**:

- **Entrada**: Recibe una descripción del método que el usuario necesita.
- **Procesamiento**:
  - Utiliza embeddings proporcionados por `AzureOpenAIEmbeddings` para convertir la descripción en un vector numérico.
  - Realiza una búsqueda vectorial y semántica en el índice `api_final` de Azure Cognitive Search para encontrar métodos relevantes.
  - Recupera hasta 15 métodos que coinciden con la descripción.
- **Salida**:
  - Devuelve una lista de métodos con su nombre, sistema y descripción breve.

**Desarrollo**:

La herramienta está implementada como una función decorada con `@tool` de LangChain, lo que la integra fácilmente en el flujo del asistente. Utiliza modelos de datos definidos con `pydantic` para validar la entrada.

**Código de la herramienta**:

```python
class method_decription(BaseModel):
    method_description: str = Field(description="Descripción de lo que el método debe hacer")

@tool("get_methods_from_description", args_schema=method_decription)
def get_methods_from_description(method_description: str):
    """Devuelve una lista de posibles métodos dada una descripción. Solo devuelve el nombre, sistema y breve descripción de los métodos."""

    vector_query = VectorizedQuery(
        vector=embeddings.embed_query(method_description),
        k_nearest_neighbors=50,
        fields="vector",
        exhaustive=True
    )
    results = search_client.search(
        search_text=method_description,
        vector_queries=[vector_query],
        select=["nombre", "sistema", "descripcion"],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='my-semantic-config',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=15,
    )
    ret_metods = []
    for res in results:
        ret_metods.append((res["nombre"], res["sistema"], res["descripcion"]))

    resp = ""
    for metod in ret_metods:
        resp += method_info_as_string(metod) + "\n"
    return resp
```

### get_method_info_from_name

Esta herramienta proporciona información detallada sobre un método específico, incluyendo su esquema de entrada y salida, posibles errores y ejemplos de llamadas utilizando SOAP o JSON.

**Funcionamiento**:

- **Entrada**: Recibe el nombre del método y el sistema al que pertenece.
- **Procesamiento**:
  - Construye un filtro para buscar exactamente el método y sistema especificados.
  - Realiza una búsqueda semántica en el índice `api_final` para recuperar la información detallada del método.
- **Salida**:
  - Devuelve información detallada del método, incluyendo su descripción, entrada, salida, errores y ejemplos.

**Desarrollo**:

Al igual que la herramienta anterior, está implementada como una función con el decorador `@tool` y utiliza modelos de datos para validar la entrada. Si el método no se encuentra, devuelve un mensaje indicando que no se encontró el método y solicita verificar el nombre y sistema proporcionados.

**Código de la herramienta**:

```python
class method_name(BaseModel):
    method: str = Field(description="Método del cual buscar información")
    sistem: str = Field(description="Sistema al que pertenece el método")

@tool("get_method_info_from_name", args_schema=method_name)
def get_method_info_from_name(method: str, sistem: str):
    """Devuelve información (esquema de entrada-salida, posibles errores y ejemplo de llamada usando SOAP o JSON) de un método."""

    filters = f"sistema eq '{sistem}' and nombre eq '{method}'"

    results = search_client.search(
        search_text="",
        select=["nombre", "sistema", "descripcion", "entrada", "salida", "error", "ej_in", "ej_out"],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name='my-semantic-config',
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=1,
        filter=filters
    )
    ret_metod = []
    for res in results:
        ret_metod.append((res["nombre"], res["sistema"], res["descripcion"], res["entrada"], res["salida"], res["error"], res["ej_in"], res["ej_out"]))
    if len(ret_metod) == 0:
        return "No se encontró el método. Por favor, verifique que el nombre del método y el sistema sean correctos."
    ret_metod = ret_metod[0]
    resp = method_info_as_string(ret_metod, params_info=True)
    return resp
```

Estas herramientas son esenciales para que el asistente proporcione respuestas precisas y detalladas sobre la documentación de la API de Bantotal, asegurando que la información esté siempre basada en fuentes confiables y actualizadas.