

from uuid import uuid4
from langsmith import Client
from dotenv import load_dotenv
from pyprojroot import here
import os



from typing import Any, List, Union

from fastapi import FastAPI
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage

from langserve import add_routes
from langserve.pydantic_v1 import BaseModel, Field


from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from asistentes.asistentes import asistente_api, asistente_core, asistente_migracion, asistente_capacitacion

# VARIABLES DE ENTORNO
dotenv_path = here() / ".env"
load_dotenv(dotenv_path=dotenv_path)

# LANGSMITH
client = Client()
os.environ["LANGCHAIN_PROJECT"] = f"ASISTENTES_CLOUD"



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

# AGREGAR RUTA POR ASISTENTE
add_routes(
    app,
    asistente_api.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
    path="/API"
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
    uvicorn.run(app, host="0.0.0.0", port=8000)