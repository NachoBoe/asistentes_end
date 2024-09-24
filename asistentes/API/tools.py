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



# VARIABLES DE ENTORNO

## envs
dotenv_path = here() / ".env"
load_dotenv(dotenv_path=dotenv_path)



# LEVANTAR DATOS


## Indices Azure Ai Search
index_name = "api_final"
credential = AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_API_KEY"))
endpoint = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002", azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), api_key=os.getenv("AZURE_OPENAI_API_KEY"))
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)




# FUNCIONES AUXILIARES
def method_info_as_string(metod,params_info=False):
    strng  = ""
    strng += f"Metodo: {metod[0]} \n Sistema: {metod[1]} \n Descripción: {metod[2]} \n "
    if params_info:
        strng  += f"{metod[3]} \n {metod[4]} \n {metod[5]} \n"
        strng  += f"{metod[6]} \n {metod[7]}"
    return strng

def remover_tildes(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')



# DEFINIR TOOLS

class sistem(BaseModel):
    sistem: str = Field(description="Sistem to which get the method")

class method_decription(BaseModel):
    method_description: str = Field(description="Description of what the method should do")

class method_name(BaseModel):
    method: str = Field(description="Method to search information of")
    sistem: str = Field(description="Sistem to which the method belongs to")



## TOOL 1
@tool("get_methods_from_description", args_schema=method_decription)
def get_methods_from_description(method_description:str):
    """ Returns a list of possible methods provided a description. It ONLY returns the name, sistem and brief description of the methods. """

    # # VECTOR SEARCH
    # if sistem != "all":
    #     search_str = f"{sistem}. {method_description}"
    # else:
    #     search_str = method_description
    vector_query = VectorizedQuery(vector=embeddings.embed_query(method_description), k_nearest_neighbors=50, fields="vector", exhaustive=True)
    results = search_client.search(  
        search_text=method_description,  
        vector_queries=[vector_query],
        select=["nombre", "sistema", "descripcion"],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=15,
    )
    ret_metods = []
    for res in results:
        ret_metods.append((res["nombre"],res["sistema"],res["descripcion"]))

    resp = ""
    for metod in ret_metods:
        resp +=  method_info_as_string(metod) + "\n"
    return resp



## TOOL 2
@tool("get_method_info_from_name", args_schema=method_name)
def get_method_info_from_name(method:str, sistem: str):
    """ Returns information (input-ouput squeema, possible errors and calling example using Soap or JSON) of a method."""

    filters = f"sistema eq '{sistem}' and nombre eq '{method}'"

    # Pure Vector Search
    results = search_client.search(  
        search_text="", 
        select=["nombre", "sistema", "descripcion", "entrada", "salida", "error", "ej_in", "ej_out"],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=1,
        filter=filters
    )
    ret_metod = []
    for res in results:
        ret_metod.append((res["nombre"],res["sistema"],res["descripcion"], res["entrada"], res["salida"], res["error"], res["ej_in"], res["ej_out"]))
    if len(ret_metod) == 0:
        return "No se encontró el método. Por favor, verifique que el nombre del método y el sistema sean correctos."
    ret_metod = ret_metod[0]
    resp =  method_info_as_string(ret_metod,params_info=True)
    return resp


# ## TOOL 3
# @tool("get_all_method_from_sistem", args_schema=sistem)
# def get_all_method_from_sistem(sistem: str="all"):
#     """ Returns all methods for a given sistem. Only returns the name, sistem and brief description of the methods. """

#     filters = f"sistema eq '{sistem}'"

#     # Pure Vector Search
#     results = search_client.search(
#         search_text="",
#         select=["nombre", "sistema", "descripcion"],
#         query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
#         top=1000,
#         filter=filters
#     )
    
#     ret_metods = []
#     for res in results:
#         ret_metods.append((res["nombre"],res["sistema"],res["descripcion"]))

#     resp = ""
#     for metod in ret_metods:
#         resp +=  method_info_as_string(metod) + "\n"
        
#     return resp



tools = [get_methods_from_description, get_method_info_from_name]#,get_all_method_from_sistem]
