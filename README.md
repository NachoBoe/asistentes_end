# Proyecto Asistentes Bantotal

Este proyecto contiene los asistentes y el código necesario para levantar un servidor con estos. 

## Ejecución Local

1. Clona este repositorio:

   ```bash
   git clone git@git.dlya.com.uy:ialabs/btasistentes.git
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno

Asegúrate de tener un archivo `.env` en el directorio raíz con las siguientes variables:

- `LOCAL`: Indica si el servidor se ejecuta localmente (`1`) o en la nube (`0`).
- `AZURE_STORAGE_KEY`: Clave de acceso para Azure Blob Storage.

Ejemplo de archivo `.env`:

```
LOCAL=1
AZURE_STORAGE_KEY=tu_clave_de_acceso
```


4. Ejecutar el servidor

```bash
python servidor.py
```

El servidor quedará corriendo en `http://localhost:8000`.


## Despliegue en Azure

Este servidor también está desplegado en Azure y puede ser accedido en la siguiente URL:

[https://btasistentes.azurewebsites.net/](https://btasistentes.azurewebsites.net/)


## Endpoints Auxiliares del Servidor

A continuación se presentan y describen como usar los enpoints auxiliares del servidor. Estos corresponden a chequeos de salud, aceptar feedback y subir/eliminar archivos para que los asistentes puedan utilizar.

### Salud del Servidor

- **URL**: `/health`
- **Método**: `GET`
- **Descripción**: Verifica si el servidor está funcionando correctamente.
- **Respuesta Exitosa**:

  - Código: `200 OK`
  - Cuerpo: `"OK"`

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

  - Código: `200 OK`
  - Cuerpo:

    ```json
    {
      "message": "File uploaded successfully and text extracted",
      "filename": "archivo.txt",
      "token_count": 1234
    }
    ```

- **Errores**:

  - Código: `400 Bad Request` si el tipo de archivo es inválido.
  - Código: `500 Internal Server Error` en caso de error interno.

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

  - Código: `200 OK`
  - Cuerpo:

    ```json
    {
      "message": "All files in the directory './uploads/123' have been deleted"
    }
    ```

- **Errores**:

  - Código: `500 Internal Server Error` en caso de error interno.

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
    "historial": Lista de tuplas ("user"/"ai" - "mensaje"),
    "endpoint": "nombre_del_endpoint"
  }
  ```

- **Respuesta Exitosa**:

  - Código: `200 OK`
  - Cuerpo:

    ```json
    {
      "message": "Feedback uploaded successfully",
      "filename": "2023-10-01_12-00-00.json"
    }
    ```

- **Errores**:

  - Código: `500 Internal Server Error` en caso de error interno.

- **Ejemplo de Uso**:

  ```bash
  curl -X POST http://localhost:8000/feedback \
    -H "Content-Type: application/json" \
    -d '{
      "isPositive": "true",
      "comentario": "Muy útil",
      "mensaje": "Consulta realizada",
      "respuesta": "Respuesta del asistente",
      "historial": [("user", "mensaje_usuario_1"), ("ai", "respuesta_ai_1")],
      "endpoint": "API_docs"
    }'
  ```

## Asistentes

Cada asistente es levantado en el servidor como un RemoteRunnable de LangServe ([https://python.langchain.com/docs/langserve/](https://python.langchain.com/docs/langserve/)). 


### Asistentes disponibles:

Estos son los agentes que quedan dispoinbles una vez que el servidor se levanta.

#### Api Docs

- descripción: Asistente que responde sobre consultas de la API de BTServices
- path: `/API_docs`


#### Migración

- descripción: Asistente que responde sobre consultas el proceso de migración a Bantotal.
- path: `/migracion`

#### Pseudo Código

- descripción: Asistente que ayuda a entender código genexus.
- path: `/pseudo_codigo`

#### Requerimientos

- descripción: Asistente que se le sube un requermiento y permite hacerle preguntas.
- path: `/requerimientos`


(LOS DE ABAJO ESTAN EN VESRION BETA)

#### Core

- descripción: Asistente que responde sobre consultas de los manuales de usuario de BTCore
- path: `/core`



#### Capacitación

- descripción: Asistente que responde a partir de videos de capacitación Bantotal
- path: `/capacitacion`


#### Instalación

- descripción: Asistente que responde sobre los manuales de instalador de BTCore.
- path: `/instalador`


### Definición de Asistentes

Los asistentes están definidos dentro de la carpeta `asistentes`. La carpeta sigue la siguiente estructura

- `asistentes/`
    - `asistente1/`
    - `asistente2/`
    - ...
    - asistentes.py
    - src.py

En cada carpeta `asistente_i/` se encuentran los prompts y tools que definen el asistente. Dentro de esta carpeta se detalla el funcionamiento de las herramientas y prompts.  

El archivo asistentes.py levanta los prompts y tools de cada asistente y lo genera. Estos luego son importados y levantados en el servidor como RemoteRunnable.

El archivo src.py contiene modificaciones a las clases bases de langchain de asistentes utilizadas en este proyecto.



## Uso de los Asistentes:

El servidor deja lavantado los asistentes como RemoteRunnables. Para utilizar estos asistentes es necesario levantar un cliente y ejecutarlos como si se estuviesen corriendo localmente.


### Levantar Cliente

En primer lugar es necesario leventar un cliente que se conecte con el asistente remoto.

#### python

```python
from langserve import RemoteRunnable

remoteChain = RemoteRunnable("https://your_hostname.com/path")
```

#### javascript

```javascript
import { RemoteRunnable } from "@langchain/core/runnables/remote";

const remoteChain = new RemoteRunnable({
  url: "https://your_hostname.com/path",
});
```

### Llamar a asistente

Luego de levantado el cliente, los asistentes se pueden utilizar como si estuviesen siendo ejecutados localmente. Por más información de como utilizar asistentes se deja referencia a langchain. [https://python.langchain.com/v0.1/docs/modules/agents/quick_start/](https://python.langchain.com/v0.1/docs/modules/agents/quick_start/)

#### python

```python
params_in = {"input": "Hola", "chat_history": []}
config = {"configurable":{"user_id": "1234"}}

# Con metodo Invoke
respuesta = remoteChain.invoke(params_in,config=config)
print(respuesta)

# Con metodo streamEvents
async for chunk in agent_executor.astream_events(params_in, version="v1",config=config):
    print(chunk)
```

#### javascript

```javascript 
const params_in = {"input": "Hola", "chat_history": []}
const config_invoke = {"configurable":{"user_id": "1234"}}
const config_stream = {"configurable":{"user_id": "1234"}}


// Con metodo Invoke
const result = await remoteChain.invoke(params_in, config_invoke);

// Con metodo streamEvents
const logStream = await remoteChain.streamEvents(
  params_in,
  config_stream
)
```
## Más Información

Por más información sobre el uso y despliegue de asistentes se deja referencia a la documentación de langchain y langserve:

Langchain: [https://python.langchain.com/docs/introduction/](https://python.langchain.com/docs/introduction/)

Langserve: [https://python.langchain.com/docs/langserve/](https://python.langchain.com/docs/langserve/)
