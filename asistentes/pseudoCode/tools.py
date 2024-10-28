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


# VARIABLES DE ENTORNO

# ## envs
# dotenv_path = here() / ".env"
# load_dotenv(dotenv_path=dotenv_path)



# DEFINIR TOOLS

@tool("empty_tool")
def empty_tool():
    """Empty tool. Do not use. Answer directly according to the system prompt."""
    return None

tools = [empty_tool]
