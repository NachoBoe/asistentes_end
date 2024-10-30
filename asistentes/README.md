# Asistentes

## Asistente en langchain
Los asistentes estan definidos mediante el uso de las funciones `create_tool_calling_agent` y `AgentExecutor` del módulo `langchain.agent`. 

El siguiente [link](https://python.langchain.com/v0.1/docs/modules/agents/quick_start/) contiene un ejemplo sencillo de como implementar un asistente utilizando estas funciones.
 
Para armar el asistente, es necesario definir tres argumentos:  

- La __llm__, la cual es el modelo de lenguaje utilizado por el asistente a la hora de responder.
- La lista de __tools__, las cuales dispone el asistente para interactuar con data fuera de la llm. 
- El __prompt__, el cual se utiliza como indicatriz para al asistente de como comportarse/responder.

## Organización de la carpeta

Esta carpeta esta organizada de la siguiente manera:

- `asistente1/`
- `asistente2/`
- ...
- `asistentes.py`
- `src.py`


### `asistente_i/`
Cada asistente tiene definida una carpeta la cual tiene dos archivos, `tools.py` y `prompts.py`, donde se define la lista de tools y el prompt a utilizar para ese asistente. 

Dentro de cada carpeta se encuentra un `README.md` que explica en detalle las tools que dispone el asistente.

### `asistentes.py`
En el archivo `asistentes.py` se define la llm a utilizar, la cual es igual en todos los asistentes y a día de hoy consiste en el modelo **gpt-4o-mini** de __OpenAI__. Luego, se importa para cada uno de los asistentes las tools y el prompt, y se define el asistente utilizando las dos funciones previamente mencionadas.

### `src.py` 

Por último, el archivo `src.py` define ciertas modificaciones de clases base de langchain para poder agregar ciertas funcionalidades necesarias. Estas son:

- __ConfigurableSearchTool__: Esta clase hereda de la clase [BaseTool](https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/#subclass-basetool), agregandose la funcionablidad de recibir una configuración de una llamada al asistente. Esto es necesario para tools que sean personalizadas segun el *user_id*, como en el asistente de requerimientos para hablar con pdf subidos por el usuario.

- __CustomAgentExecutor__: Esta clase presenta una leve modificación de la clase AgentExecutor, permitiendo propagar la configuración recibida en la llamada del asistente a las tools. Junto a la modificación anterior, permite configurar con parametros unicos a las tools en cada llamada al asistente. 


Estos cambios fueron necesarios porque los agentes no propagan naturalmente las configuraciones a las tools. El siguiente issue de github explica en detalle este problema. [https://github.com/langchain-ai/langchain/discussions/17555](https://github.com/langchain-ai/langchain/discussions/17555)

- __CostCalcCallbackHandler__:  Esta clase hereda de [AsyncCallbackHandler](https://python.langchain.com/v0.1/docs/modules/callbacks/async_callbacks/) y permite calcular el número de tokens de cada interacción con el modelo y loguearlas a un servidor de costos. Al inicio de una llamada a la llm, se contabilizan los tokens del prompt y se envían a un endpoint para registrar el costo de la interacción. Similarmente, al finalizar la llamada a la llm, se registran los tokens generados por el modelo. Cada vez que se termina la llamada al asistente (que puede implicar varias llamadas a la llm), la clase registra los tokens de entrada y salida, enviando la información al endpoint /add_trace del servidor configurado. Para habilitar esta funcionalidad, la variable de entorno `LOGGEO_COSTO` debe ser igual a `1` y la ruta del servidor debe estar especificada en la variable de entorno `LOGGEO_COSTO_ENDPOINT`.



## AZURE AI SEARCH

Los asistentes en este proyecto se basan principalmente en el uso de RAG (Retrieval-Augmented Generation), una técnica que combina busqueda de información relevante en bases de datos vectoriales para aumentar las respuestas que proporcionan los asistentes a las preguntas del usuario. En este proyecto, se emplean las bases vectoriales de Azure AI Search, conocidas como *indexes*. No es necesario conocer su funcionamiento para utilizar los asistentes existentes, sin embargo es necesario para crear nuevos asistentes. 

Para la creación de estos índices en Azure Search utilizando python, puedes consultar el siguiente repositorio de Microsoft Azure: [sample_index_crud_operations.py](https://github.com/Azure/azure-sdk-for-python/blob/7cd31ac01fed9c790cec71de438af9c45cb45821/sdk/search/azure-search-documents/samples/sample_index_crud_operations.py). 

Asimismo, para realizar consultas sobre estos índices y obtener resultados relevantes utilizando python, puedes consultar el ejemplo de consultas disponible en este repositorio: [demo-python](https://github.com/Azure/azure-search-vector-samples/tree/main/demo-python). 
