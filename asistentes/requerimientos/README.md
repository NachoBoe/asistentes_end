# Asistente para Analistas de Bantotal

## Descripción

Este asistente está diseñado para ayudar a los programadores analistas de Bantotal a comprender el desarrollo de un requerimiento en Genexus. Proporciona información relevante basada en las solicitudes del usuario y el contenido del documento de requerimientos que el usuario haya subido. El usuario puede cargar un documento que contenga toda la información sobre el requerimiento y hacer preguntas específicas sobre este archivo. El asistente accederá al documento utilizando la herramienta correspondiente y responderá en español de manera clara, precisa y detallada, utilizando únicamente la información proporcionada en el documento, el historial del chat y su conocimiento previo sobre Genexus y Bantotal.

Si el usuario no ha subido un documento o el documento no es un requerimiento válido, el asistente informará al usuario en consecuencia. Además, al final de cada respuesta y separado por un salto de línea, el asistente indicará el número de página de donde extrajo la información para facilitar la referencia.

## Herramientas

### getDocument

Esta herramienta recupera el documento completo que el usuario ha subido (si existe). Permite al asistente acceder al contenido del documento para responder a las preguntas del usuario.

**Funcionamiento**: La herramienta intenta leer el contenido del archivo ubicado en una ruta específica basada en el ID del usuario (`uploads/{user_id}/archivo.txt`). Si el archivo existe, devuelve el contenido completo del documento. Si el archivo no existe, devuelve un mensaje indicando que no se ha subido ningún documento.

**Desarrollo**: La herramienta está implementada como una clase llamada `CustomTool` que hereda de `ConfigurableSearchTool`. Utiliza un esquema de entrada vacío (`EmptyInput`), ya que no requiere parámetros adicionales para su ejecución. La clase define los métodos `_run` y `_arun` para permitir la ejecución síncrona y asíncrona, respectivamente, adaptándose a diferentes contextos dentro del asistente.

```python
class CustomTool(ConfigurableSearchTool):
    name = "getDocument"
    description = "Recupera el documento completo subido por el usuario (si existe)."
    args_schema: Type[BaseModel] = EmptyInput
    config = {}
    
    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        config = self.config["configurable"]
        path = "uploads/" + config["user_id"] + "/archivo.txt"
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc_content = f.read()
        except:
            doc_content = "No se ha subido ningún documento."   
        return doc_content

    async def _arun(self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        config = self.config["configurable"]
        path = "uploads/" + config["user_id"] + "/archivo.txt"
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc_content = f.read()
        except:
            doc_content = "No se ha subido ningún documento."   
        return doc_content
```