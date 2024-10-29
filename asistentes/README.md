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

Dentro de cada carpeta se encuentra un README que explica en detalle las tools que dispone el asistente.

### `asistentes.py`
En el archivo `asistentes.py` se define la llm a utilizar, la cual es igual en todos los asistentes y a día de hoy consiste en el modelo **gpt-4o-mini** de _OpenAI_. Luego, se importa para cada uno de los asistentes las tools y el prompt, y se define el asistente utilizando las dos funciones previamente mencionadas.

### `src.py` 

Por último, el archivo `src.py` define ciertas modificaciones de clases base de langchain para poder agregar ciertas funcionalidades necesarias. Estas son:

- __ConfigurableSearchTool__: Esta clase hereda de la clase [BaseTool](https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/#subclass-basetool), agregandose la funcionablidad de recibir una configuración de una llamada al asistente. Esto es necesario para tools que sean personalizadas segun el *user_id*, como en el asistente de requerimientos para hablar con pdf subidos por el usuario.

- __CustomAgentExecutor__: Esta clase presenta una leve modificación de la clase AgentExecutor, permitiendo propagar la configuración recibida en la llamada del asistente a las tools. Junto a la modificación anterior, permite configurar con parametros unicos a las tools en cada llamada al asistente. 


Estos cambios fueron necesarios porque los agentes no propagan naturalmente las configuraciones a las tools. El siguiente issue de github explica en detalle este problema. [https://github.com/langchain-ai/langchain/discussions/17555](https://github.com/langchain-ai/langchain/discussions/17555)