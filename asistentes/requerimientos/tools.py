# IMPORTS

## variables de entorno
from dotenv import load_dotenv
from pyprojroot import here
import os
## Tools langchain
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
## Data local
import unicodedata
import dill
## Azure Ai Search
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_openai import AzureOpenAIEmbeddings
import tiktoken
from langchain_core.runnables import ConfigurableField, RunnableSerializable
from langchain_core.runnables.config import RunnableConfig
from langchain_community.document_loaders import PyPDFLoader


# VARIABLES DE ENTORNO

## envs
dotenv_path = here() / ".env"
load_dotenv(dotenv_path=dotenv_path)



from typing import Optional, Type, Dict

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

from asistentes.src import ConfigurableSearchTool

class EmptyInput(BaseModel):
    pass


class CustomTool(ConfigurableSearchTool):
    name = "getDocument"
    description = "Retrieves the complete document uploaded by the user (if it exists)."
    args_schema: Type[BaseModel] = EmptyInput
    config = {}
    
    def _run(
        self,run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        config = self.config["configurable"]
        path = "uploads/" + config["user_id"] + "/archivo.txt"
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc_content = f.read()
        except:
            doc_content = "No se ha subido ningún documento."   
        return doc_content

    async def _arun(
        self,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        config = self.config["configurable"]
        path = "uploads/" + config["user_id"] + "/archivo.txt"
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc_content = f.read()
        except:
            doc_content = "No se ha subido ningún documento."   
        return doc_content
    
    
    
tools = [CustomTool()]
