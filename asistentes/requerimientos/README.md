# Asistente para Analisís de Requerimientos de Bantotal

## Descripción

Este asistente está diseñado para ayudar a comprender el desarrollo de un requerimiento. Responde consultas sobre el requerimiento, como función, la solución propuesta, etc. Para poder utilizar este asistente es necesario subir un requerimiento en formato _.pdf_ o _.docx_

## Herramientas

### getDocument

Esta herramienta recupera el contenido documento completo que el usuario ha subido (si existe). Permite al asistente acceder al contenido del documento para responder a las preguntas del usuario.

**Funcionamiento**: La herramienta intenta leer el contenido del archivo ubicado en una ruta específica basada en el ID del usuario (`uploads/{user_id}/archivo.txt`). Si el archivo existe, devuelve el contenido completo del documento. Si el archivo no existe, devuelve un mensaje indicando que no se ha subido ningún documento.
