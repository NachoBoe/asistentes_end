# Proyecto Asistentes Bantotal

Este proyecto incluye los asistentes y el código necesario para levantar un servidor con ellos.

## Ejecución Local

### Clona este repositorio:

   ```bash
   git clone git@git.dlya.com.uy:ialabs/btasistentes.git
   ```

### Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

### Variables de Entorno

   Asegúrate de tener un archivo `.env` en el directorio raíz con las siguientes variables:

   - `LOCAL`: Indica si el servidor se ejecuta localmente (`1`) o en Azure (`0`).
   - `LANGCHAIN_TRACING_V2`: Activa el tracing para Langsmith (`true` o `false`).
   - `LANGCHAIN_ENDPOINT`: Endpoint para Langsmith.
   - `LANGCHAIN_API_KEY`: Clave de API para Langsmith.
   - `OPENAI_API_KEY`: Clave de API para Azure OpenAI (generación de texto).
   - `AZURE_OPENAI_API_KEY`: Clave de API para Azure OpenAI (embeddings).
   - `AZURE_OPENAI_ENDPOINT`: Endpoint para Azure OpenAI.
   - `OPENAI_API_VERSION`: Versión de la API de OpenAI.
   - `AZURE_AI_SEARCH_SERVICE_NAME`: Nombre del servicio Azure Search.
   - `AZURE_AI_SEARCH_API_KEY`: Clave de API para Azure Search.
   - `AZURE_STORAGE_KEY`: Clave de acceso para Azure Blob Storage.

   **Ejemplo de archivo `.env`:**

   ```ini
   # Indica si se corre localmente (1) o en Azure (0)
   LOCAL=1

   # Langsmith para el tracing
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGCHAIN_API_KEY=tu_langchain_api_key

   # Azure OpenAI para generación de texto
   OPENAI_API_KEY=tu_openai_api_key

   # Azure OpenAI para embeddings
   AZURE_OPENAI_API_KEY=tu_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=tu_azure_openai_endpoint
   OPENAI_API_VERSION="2023-12-01-preview"

   # Azure Search para herramientas que se usan en el asistente
   AZURE_AI_SEARCH_SERVICE_NAME=tu_azure_search_service_name
   AZURE_AI_SEARCH_API_KEY=tu_azure_search_api_key

   # Azure Storage para guardar el feedback
   AZURE_STORAGE_KEY=tu_azure_storage_key
   ```

   **Nota:** Reemplaza `tu_langchain_api_key`, `tu_openai_api_key`, `tu_azure_openai_api_key`, `tu_azure_search_api_key` y `tu_azure_storage_key` con tus claves de API reales. Asegúrate de mantener estas claves seguras y no compartirlas públicamente.

### Ejecuta el servidor:

   ```bash
   python servidor.py
   ```

   El servidor quedará corriendo en `http://localhost:8000`.

## Despliegue en Azure

Este servidor también está desplegado en Azure y puede ser accedido en la siguiente URL:

[https://btasistentes.azurewebsites.net/](https://btasistentes.azurewebsites.net/)

## Endpoints Auxiliares del Servidor

A continuación se presentan y describen cómo usar los endpoints auxiliares del servidor. Estos permiten realizar chequeos de salud, aceptar feedback y subir/eliminar archivos que los asistentes pueden utilizar.

### Salud del Servidor

- **URL**: `/health`
- **Método**: `GET`
- **Descripción**: Verifica si el servidor está funcionando correctamente.
- **Respuesta Exitosa**:

  - **Código**: `200 OK`
  - **Cuerpo**: `"OK"`

- **Ejemplo de Uso**:

  ```bash
  curl -X GET http://localhost:8000/health
  ```

### Subir Archivos

- **URL**: `/upload`
- **Método**: `POST`
- **Descripción**: Permite subir archivos PDF, DOCX u ODT, extrae el texto y lo guarda en un archivo `.txt`.
- **Parámetros**:

  - `userId` (form data): ID del usuario.
  - `file` (form data): Archivo a subir.

- **Respuesta Exitosa**:

  - **Código**: `200 OK`
  - **Cuerpo**:

    ```json
    {
      "message": "Archivo subido correctamente y texto extraído",
      "filename": "archivo.txt",
      "token_count": 1234
    }
    ```

- **Errores**:

  - **Código**: `400 Bad Request` si el tipo de archivo es inválido.
  - **Código**: `500 Internal Server Error` en caso de error interno.

- **Ejemplo de Uso**:

  ```bash
  curl -X POST http://localhost:8000/upload \
    -F "userId=123" \
    -F "file=@/ruta/al/archivo.pdf"
  ```

### Eliminar Archivos

- **URL**: `/delete_files`
- **Método**: `DELETE`
- **Descripción**: Elimina todos los archivos del directorio de un usuario específico.
- **Parámetros**:

  - `userId` (form data): ID del usuario.

- **Respuesta Exitosa**:

  - **Código**: `200 OK`
  - **Cuerpo**:

    ```json
    {
      "message": "Todos los archivos en el directorio del usuario '123' han sido eliminados"
    }
    ```

- **Errores**:

  - **Código**: `500 Internal Server Error` en caso de error interno.

- **Ejemplo de Uso**:

  ```bash
  curl -X DELETE http://localhost:8000/delete_files \
    -F "userId=123"
  ```

### Enviar Feedback

- **URL**: `/feedback`
- **Método**: `POST`
- **Descripción**: Recibe feedback y lo guarda en Azure Blob Storage.
- **Cuerpo de la Solicitud** (JSON):

  ```json
  {
    "isPositive": "true",
    "comentario": "Muy útil",
    "mensaje": "Consulta realizada",
    "respuesta": "Respuesta obtenida",
    "historial": [
      {"role": "user", "message": "mensaje_usuario_1"},
      {"role": "ai", "message": "respuesta_ai_1"}
    ],
    "endpoint": "nombre_del_endpoint"
  }
  ```

- **Respuesta Exitosa**:

  - **Código**: `200 OK`
  - **Cuerpo**:

    ```json
    {
      "message": "Feedback subido correctamente",
      "filename": "2023-10-01_12-00-00.json"
    }
    ```

- **Errores**:

  - **Código**: `500 Internal Server Error` en caso de error interno.

- **Ejemplo de Uso**:

  ```bash
  curl -X POST http://localhost:8000/feedback \
    -H "Content-Type: application/json" \
    -d '{
      "isPositive": "true",
      "comentario": "Muy útil",
      "mensaje": "Consulta realizada",
      "respuesta": "Respuesta del asistente",
      "historial": [
        {"role": "user", "message": "mensaje_usuario_1"},
        {"role": "ai", "message": "respuesta_ai_1"}
      ],
      "endpoint": "API_docs"
    }'
  ```

## Asistentes

Cada asistente es levantado en el servidor como un `RemoteRunnable` de LangServe ([https://python.langchain.com/docs/langserve/](https://python.langchain.com/docs/langserve/)).

### Asistentes Disponibles

Estos son los agentes que están disponibles una vez que el servidor está en ejecución.

#### API Docs

- **Descripción**: Asistente que responde sobre consultas de la API de BTServices.
- **Path**: `/API_docs`

#### Migración

- **Descripción**: Asistente que responde sobre consultas del proceso de migración a Bantotal.
- **Path**: `/migracion`

#### Pseudo Código

- **Descripción**: Asistente que ayuda a entender código GeneXus.
- **Path**: `/pseudo_codigo`

#### Requerimientos

- **Descripción**: Asistente al que se le sube un requerimiento y permite hacerle preguntas.
- **Path**: `/requerimientos`

#### Nota: Los siguientes asistentes están en versión BETA.

#### Core

- **Descripción**: Asistente que responde sobre consultas de los manuales de usuario de BTCore.
- **Path**: `/core`

#### Capacitación

- **Descripción**: Asistente que responde a partir de videos de capacitación Bantotal.
- **Path**: `/capacitacion`

#### Instalación

- **Descripción**: Asistente que responde sobre los manuales del instalador de BTCore.
- **Path**: `/instalador`

### Definición de Asistentes

Los asistentes están definidos dentro de la carpeta `asistentes`. La carpeta sigue la siguiente estructura:

- `asistentes/`
  - `asistente1/`
  - `asistente2/`
  - ...
  - `asistentes.py`
  - `src.py`

En cada carpeta `asistente_i/` se encuentran los prompts y herramientas que definen el asistente. Dentro de esta carpeta se detalla el funcionamiento de las herramientas y prompts.

El archivo `asistentes.py` carga los prompts y herramientas de cada asistente y los genera. Estos luego son importados y ejecutados en el servidor como `RemoteRunnable`.

El archivo `src.py` contiene modificaciones a las clases base de asistentes de LangChain utilizadas en este proyecto.

## Uso de los Asistentes

El servidor expone los asistentes como `RemoteRunnable`. Para utilizarlos, es necesario iniciar un cliente y ejecutarlos como si se estuvieran corriendo localmente.

### Iniciar Cliente

En primer lugar, es necesario iniciar un cliente que se conecte con el asistente remoto.

#### Python

```python
from langserve import RemoteRunnable

remoteChain = RemoteRunnable("https://your_hostname.com/path")
```

#### JavaScript

```javascript
import { RemoteRunnable } from "@langchain/core/runnables/remote";

const remoteChain = new RemoteRunnable({
  url: "https://your_hostname.com/path",
});
```

### Llamar al Asistente

Una vez iniciado el cliente, los asistentes se pueden utilizar como si se estuviesen ejecutando localmente. Para más información sobre cómo utilizar asistentes, consulta la documentación de LangChain: [https://python.langchain.com/v0.1/docs/modules/agents/quick_start/](https://python.langchain.com/v0.1/docs/modules/agents/quick_start/)

#### Python

```python
params_in = {"input": "Hola", "chat_history": []}
config = {"configurable": {"user_id": "1234"}}

# Con método invoke
respuesta = remoteChain.invoke(params_in, config=config)
print(respuesta)

# Con método astream_events
async for chunk in remoteChain.astream_events(params_in, config=config):
    print(chunk)
```

#### JavaScript

```javascript
const params_in = { input: "Hola", chat_history: [] };
const config_invoke = { configurable: { user_id: "1234" } };
const config_stream = { configurable: { user_id: "1234" } };

// Con método invoke
const result = await remoteChain.invoke(params_in, config_invoke);

// Con método streamEvents
const logStream = await remoteChain.streamEvents(
  params_in,
  config_stream
);
```

## Más Información

Para más información sobre el uso y despliegue de asistentes, consulta la documentación de LangChain y LangServe:

- **LangChain**: [https://python.langchain.com/docs/introduction/](https://python.langchain.com/docs/introduction/)
- **LangServe**: [https://python.langchain.com/docs/langserve/](https://python.langchain.com/docs/langserve/)