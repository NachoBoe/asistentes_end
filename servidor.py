

from uuid import uuid4
from langsmith import Client
from dotenv import load_dotenv
from pyprojroot import here
import os



from typing import Any, List, Union, Tuple

from fastapi import FastAPI, HTTPException, Request
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage

from langserve import add_routes
from langserve.pydantic_v1 import BaseModel, Field


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from asistentes.asistentes import asistente_api, asistente_core, asistente_migracion, asistente_capacitacion

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureNamedKeyCredential
import json
import datetime
import os
# VARIABLES DE ENTORNO
dotenv_path = here() / ".env"


# LANGSMITH
client = Client()


if int(os.environ["LOCAL"]) == 1:
    HOST = "127.0.0.1"
    os.environ["LANGCHAIN_PROJECT"] = f"ASISTENTES_LOCAL"
else:
    os.environ["LANGCHAIN_PROJECT"] = f"ASISTENTES_CLOUD"
    HOST = "0.0.0.0"


# LEVANTAR SERVIDOR

app = FastAPI(
    title="Server Asistentes Bantotal",
    version="1.0",
    description="Servidor que mantiene asistentes de Bantotal",
)

origins = ["http://localhost", "http://localhost:9000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Input(BaseModel):
    input: str
    chat_history: List[Union[HumanMessage, AIMessage, FunctionMessage]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "input", "output": "output"}},
    )


class Output(BaseModel):
    output: Any

# AGREGAR RUTA THE /HEALTH
@app.get("/health")
def health_check():
    return 'OK'




credential = AzureNamedKeyCredential("btalmacenamientoai", os.getenv("AZURE_STORAGE_KEY"))
blob_service_client = BlobServiceClient("https://btalmacenamientoai.blob.core.windows.net", credential=credential)

class Feedback(BaseModel):
    isPositive: str
    comentario: str
    mensaje: str
    respuesta: str
    historial: List[List[str]]
    endpoint: str
    
@app.post("/feedback")
async def feedback(request: Request):
    try:
        # Parse the incoming JSON payload
        json_data = await request.json()
        
        # Log the received JSON data for debugging
        print("Received JSON data:", json_data)
        
        feedback = Feedback(**json_data)

        local_path = "./" + feedback.endpoint
        # Genera el nombre del archivo basado en la fecha y hora actuales
        local_file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        print(local_file_name, local_path)
        upload_file_path = os.path.join(local_path, local_file_name)
        print(upload_file_path)
        # Crea un directorio local si no existe
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        # Guarda el JSON recibido en un archivo local
        with open(upload_file_path, "w") as file:
            json.dump(feedback.dict(), file)

        # Crea un blob client usando el nombre del archivo local
        blob_client = blob_service_client.get_blob_client(container="feedback", blob=local_file_name)

        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Sube el archivo al blob de Azure Storage
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)
        return {"message": "Feedback uploaded successfully", "filename": local_file_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AGREGAR RUTA POR ASISTENTE
add_routes(
    app,
    asistente_api.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/APIdocs"
)


add_routes(
    app,
    asistente_core.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/core"
)

add_routes(
    app,
    asistente_migracion.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/migracion"
)

add_routes(
    app,
    asistente_capacitacion.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/capacitacion"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8000)