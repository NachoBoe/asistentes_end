# Proyecto Asistentes Bantotal

Este proyecto incluye los asistentes y el código necesario para levantar un servidor con ellos.

## Indice

1. [Indice](#indice)
2. [Ejecución Local](#ejecución-local)
   - [Clona este repositorio](#clona-este-repositorio)
   - [Instala las dependencias](#instala-las-dependencias)
   - [Variables de Entorno](#variables-de-entorno)
   - [Ejecuta el servidor](#ejecuta-el-servidor)
3. [Despliegue en Azure](#despliegue-en-azure)
4. [Endpoints Auxiliares del Servidor](#endpoints-auxiliares-del-servidor)
   - [Salud del Servidor](#salud-del-servidor)
   - [Subir Archivos](#subir-archivos)
   - [Eliminar Archivos](#eliminar-archivos)
   - [Enviar Feedback](#enviar-feedback)
5. [Logueo de Costos](#servidor-para-logueo-de-costos)
   - [Ejecutar el Servidor de Logueo](#ejecutar-el-servidor-de-logueo)
   - [Endpoints del Servidor de Logueo](#endpoints-del-servidor-de-logueo)
6. [Asistentes](#asistentes)
   - [Asistentes Disponibles](#asistentes-disponibles)
   - [Definición de Asistentes](#definición-de-asistentes)
7. [Uso de los Asistentes](#uso-de-los-asistentes)
   - [Iniciar Cliente](#iniciar-cliente)
   - [Llamar al Asistente](#llamar-al-asistente)
8. [Más Información](#más-información)


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
- `LOGGEO_COSTO`: Indica si se loguea el costo (`1`) o no (`0`).
- `LOGGEO_COSTO_ENDPOINT`: URL del servidor donde se loguea el costo.

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

# Loggeo de costo
LOGGEO_COSTO=1
LOGGEO_COSTO_ENDPOINT=http://127.0.0.1:8001
```

**Nota:** Reemplaza `tu_langchain_api_key`, `tu_openai_api_key`, `tu_azure_openai_api_key`, `tu_azure_search_api_key`, `tu_azure_storage_key` y demás claves con tus valores reales. Asegúrate de mantener estas claves seguras y no compartirlas públicamente.

### Ejecuta el servidor:

```bash
python servidor.py
```

El servidor quedará corriendo en `http://localhost:8000`.

## Despliegue en Azure

Este servidor también está desplegado en Azure y puede ser accedido en  [https://btasistentes.azurewebsites.net/](https://btasistentes.azurewebsites.net/)

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

## Servidor para Logueo de Costos

Se tiene implementada una funcionalidad que permite registrar los costos asociados al uso de los asistentes. Esta permite mantener un registro de la cantidad de tokens utilizados por cliente para cada asistente. 

Se deja disponible un ejemplo de servidor para hacer uso de esta funcionalidad. Para el funcionamiento correcto asegurarse que el servidor de asistentes fue levantado con las variables de entorno:

- `LOGGEO_COSTO`: `1`
- `LOGGEO_COSTO_ENDPOINT`: `http://127.0.0.1:8001`


Se ha agregado al proyecto un ejemplo de servidor sencillo (`cliente-servidor.py`) que recibe y almacena los registros de costos. Este servidor se ejecuta localmente y está configurado para escuchar en el puerto `8001`.

El servidor está implementado utilizando FastAPI y SQLAlchemy para manejar solicitudes y almacenar los datos en una base de datos SQLite.

- **Funcionalidades:**
  - **Agregar Registro de Costo:** Recibe datos sobre el asistente utilizado, el usuario, la fecha y los tokens de entrada y salida.
  - **Ver Registros de Costos:** Permite visualizar todos los registros almacenados en formato JSON o a través de una interfaz HTML simple.

### Ejecutar el Servidor de Logueo

1. **Instalar Dependencias:**

   Asegúrate de tener instaladas las siguientes dependencias:

   ```bash
   pip install fastapi sqlalchemy uvicorn
   ```

2. **Ejecutar el Servidor:**

   Ejecuta el script `cost_server.py`:

   ```bash
   python cost_server.py
   ```

   El servidor se ejecutará en `http://127.0.0.1:8001`.

### Endpoints del Servidor de Logueo

- **Agregar Registro de Costo:**

  - **URL**: `/add_trace`
  - **Método**: `POST`
  - **Descripción**: Permite agregar un nuevo registro de costo.
  - **Cuerpo de la Solicitud** (JSON):

    ```json
    {
      "asistente": "nombre_del_asistente",
      "usuario": "id_del_usuario",
      "date": "2023-10-01T12:00:00",
      "tokens_in": 100,
      "tokens_out": 150
    }
    ```

- **Ver Registros de Costos (JSON):**

  - **URL**: `/view_traces`
  - **Método**: `GET`
  - **Descripción**: Devuelve todos los registros de costos en formato JSON.

- **Ver Registros de Costos (HTML):**

  - **URL**: `/`
  - **Método**: `GET`
  - **Descripción**: Muestra una tabla HTML con todos los registros de costos.

Por lo tanto, accediendo en el navegador a la url http://127.0.0.1:8001 se podra ver el loggeo de los traces.


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