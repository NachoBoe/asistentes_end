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

## envs
dotenv_path = here() / ".env"
load_dotenv(dotenv_path=dotenv_path)



# LEVANTAR DATOS

## Azure AI search

embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002")
index_name = "usuarios2"
credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_API_KEY"])
endpoint = "https://bantotalsearchai.search.windows.net"
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)




# FUNCIONES AUXILIARES

def remover_tildes(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')




# DEFINIR TOOLS

class screen_class(BaseModel):
    screen_code : str = Field(description="Screen code. It is an alphanumeric identifier that usually starts with 'H' or 'W'")
    system: str = Field(description="Sistem which the method belongs to", default="")

class description_class(BaseModel):
    description: str = Field(description="Description of the functionality of the screen.")

class systems_class(BaseModel):
    system: str = Field(description="System to retrieve the screens.")


@tool("screen_from_description", args_schema=description_class)
def screen_from_description(description:str):
    """ Semantic Search engine that retrieves top 5 screen whose functionality match the description. Retrieves the screen code, description, and the system it belongs to. """

    embedding = embeddings.embed_query(description)
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields="description_vector", exhaustive=True)


    results = search_client.search(  
        search_text=description,  
        vector_queries=[vector_query],
        select=["id", "descripcion","codigo_panel", "sistema"],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=10,
        # filter="search.in(system, )",
    )

    ans = ""
    for result in results:
        ans += f"Código de Panel (Screen code): {result['codigo_panel']} \n"
        ans += f"Sistema: {result['sistema']} \n"
        ans += f"Descripcion: {result['descripcion']} \n"
        ans += "\n\n"
    return ans



@tool("step_by_step_of_screen", args_schema=screen_class)
def step_by_step_of_screen(screen_code:str, system:str= ""):
    """ Semantic Search engine that retrieves the step by step of how to use the screen, provided the screen (panel) code and the system it belongs to. """

    filter = f"codigo_panel eq '{screen_code.upper()}'"
    if system != "":
        filter += f" and sistema eq '{system}'"
    results = search_client.search(  
        search_text= f"Quiero saber sobre el panel {screen_code} del sistema {system}",  
        select=["id", "contenido","sistema","codigo_panel" ],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=1,
        filter=filter,
    )

    ans = ""
    for result in results:
        ans += f"Panel (screen): {result['codigo_panel']} \n"
        ans += f"Sistema: {result['sistema']} \n"
        ans += f"Información: {result['contenido']} \n"
        ans += "\n\n"
    if ans == "":
        ans = "No se encontraron resultados para la pantalla solicitada."
    return ans


@tool("screens_from_system", args_schema=systems_class)
def screens_from_system(system:str):
    """ Returns the list of all screens from a system. For each of them retrieves the screen code and a brief description of it functionality."""

    filter = f"sistema eq '{system}'"
    results = search_client.search(  
        search_text= f"",  
        select=["id", "descripcion","sistema","codigo_panel" ],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        filter=filter,
    )

    ans = ""
    for result in results:
        ans += f"Panel (screen): {result['codigo_panel']} \n"
        ans += f"Descripcion: {result['descripcion']} \n"
        ans += "\n\n"
    return ans


def count_tokens(text: str) -> int:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)


tools = [screen_from_description, step_by_step_of_screen, screens_from_system]
