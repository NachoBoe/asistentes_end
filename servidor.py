

from uuid import uuid4
from langsmith import Client
from dotenv import load_dotenv
from pyprojroot import here
import os



from typing import Any, List, Union, Dict

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage

from langserve import add_routes
from langserve.pydantic_v1 import BaseModel, Field


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from asistentes.asistentes import asistente_api, asistente_core, asistente_migracion, asistente_capacitacion, asistente_pseudoCode, asistente_requerimientos

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureNamedKeyCredential
import json
import datetime
import os
import fitz  # PyMuPDF for PDF parsing
import docx2txt  # for DOCX parsing
from odf.opendocument import load as load_odt  # for ODT parsing
from odf.text import P
import tiktoken

# VARIABLES DE ENTORNO
dotenv_path = "./.env"
load_dotenv(dotenv_path=dotenv_path)

print(os.environ["LOCAL"])
# LANGSMITH
client = Client()

tokenizer = tiktoken.get_encoding("cl100k_base")

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




def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    return docx2txt.process(file_path)

def extract_text_from_odt(file_path: str) -> str:
    textdoc = load_odt(file_path)
    all_text = ""
    for element in textdoc.getElementsByType(P):
        all_text += element.firstChild.data + "\n"
    return all_text


@app.post("/upload")
async def upload_file(userId: str = Form(...), file: UploadFile = File(...)):
    try:
        # Verify file type
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.oasis.opendocument.text"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and ODT files are allowed.")

        # Define the directory path based on the user ID
        upload_dir = f"./uploads/{userId}"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the file temporarily
        file_extension = os.path.splitext(file.filename)[1]
        file.filename = "archivo" + file_extension
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Extract text based on the file type
        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(file_path)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(file_path)
        elif file.content_type == "application/vnd.oasis.opendocument.text":
            text = extract_text_from_odt(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        # Remove the temporary file
        os.remove(file_path)
        
        # Save extracted text as .txt
        txt_filename = "archivo.txt"
        txt_path = os.path.join(upload_dir, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        # Count tokens using tiktoken for GPT-4o-mini
        tokens = tokenizer.encode(text)
        token_count = len(tokens)

        if token_count > 20000:
            return {"message": "Document is too long, exceeding 20,000 tokens", "token_count": token_count}

        return {"message": "File uploaded successfully and text extracted", "filename": txt_filename, "token_count": token_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

@app.delete("/delete_files")
async def delete_files(userId: str = Form(...)):
    try:
        # Define the directory path based on the user ID
        upload_dir = f"./uploads/{userId}"

        if not os.path.exists(upload_dir):
            return {"message": f"All files in the directory '{upload_dir}' have been deleted"}

        # Delete all files in the directory
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

        return {"message": f"All files in the directory '{upload_dir}' have been deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
    
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



async def per_req_config_modifier(config: Dict, request: Request) -> Dict:
    """Modify the config for each request."""
    req = await request.json()
    if "configurable" not in config.keys():
        config["configurable"] = {}
    for conf in req["config"]["configurable"].keys():
        config["configurable"][conf] = req["config"]["configurable"][conf]
    print(config)
    return config
    
    
# AGREGAR RUTA POR ASISTENTE
add_routes(
    app,
    asistente_api.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/APIdocs",
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

add_routes(
    app,
    asistente_pseudoCode.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/pseudoCode",
)

add_routes(
    app,
    asistente_requerimientos.with_types(input_type=Input, output_type=Output),
    path="/requerimientos",
    per_req_config_modifier=per_req_config_modifier
)    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8000)