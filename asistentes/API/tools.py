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

## Archivos Locales
with open('./asistentes/API/data/metodos_obj_str.pkl', 'rb') as archivo:
    metodos_lista = dill.load(archivo)

## Indices Azure Ai Search
index_name = "api11"
credential = AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_API_KEY"))
endpoint = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002", azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), api_key=os.getenv("AZURE_OPENAI_API_KEY"))
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)




# FUNCIONES AUXILIARES
def method_info_as_string(metod,params_info=False):
    strng  = ""
    strng += f"Metodo: {metod.nombre} \n Sistema: {metod.sistema} \n Descripción: {metod.descripcion} \n "
    if params_info:
        strng  += f"{metod.entrada} \n {metod.salida} \n {metod.error} \n"
        strng  += f"{metod.ej_in} \n {metod.ej_out}"
    return strng

def remover_tildes(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')



# DEFINIR TOOLS

class sistem(BaseModel):
    sistem: str = Field(description="Sistem to which get the method")

class method_decription(BaseModel):
    method_description: str = Field(description="Description of what the method should do")
    sistem: str = Field(description="Sistem to which the method belongs to", default="all")

class method_name(BaseModel):
    method: str = Field(description="Method to search information of")
    sistem: str = Field(description="Sistem to which the method belongs to", default="all")



## TOOL 1
@tool("get_methods_from_description", args_schema=method_decription)
def get_method(method_description:str, sistem: str="all"):
    """ Returns a list of possible methods provided a description. The parameter sistem is used to filter the search of the methods to a given sistem"""

    # VECTOR SEARCH
    vector_query = VectorizedQuery(vector=embeddings.embed_query(method_description), k_nearest_neighbors=30, fields="content_vector", exhaustive=True)
    results = search_client.search(  
        search_text=method_description,  
        vector_queries=[vector_query],
        select=["id", "content"],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=15,
    )
    ret_metods = []
    for res in results:
        ret_metods.append(res["id"])
    ret_metods = list(set(ret_metods))

    # QUEADARSE CON LOS METODOS 
    ret_metodos_obj = []
    indices_list = []
    for met in metodos_lista:
        if "BT" + met.sistema + "_" + met.nombre in ret_metods:
            ret_metodos_obj.append(met)
            indices_list.append(ret_metods.index("BT" + met.sistema + "_" + met.nombre))

    ret_metodos_obj_orden = sorted(zip(indices_list, ret_metodos_obj))
    ret_metodos_obj = [elemento for valor, elemento in ret_metodos_obj_orden]

    resp = ""
    for metod in ret_metodos_obj:
        resp +=  method_info_as_string(metod) + "\n"
    return resp



## TOOL 2
@tool("get_method_info_from_name", args_schema=method_name)
def get_method_info(method:str, sistem: str="all"):
    """ Returns information (input-ouput squeema, possible errors and calling example using Soap or JSON) of a method. The parameter sistem is used to filter the search of the method to a given sistem """

    # Search for the method exactly
    possible_methods = []
    for met in metodos_lista:
        if met.nombre.lower().strip() == method.lower().strip():
            possible_methods.append(met)
    
    if len(possible_methods) > 1 and sistem != "all":
        ret_metodos_obj = []
        for met in possible_methods:
            if met.sistema.lower().strip() == sistem.lower().strip():
                ret_metodos_obj.append(met)
    else:
        ret_metodos_obj = possible_methods

    # In case exact match doesnt work
    if len(ret_metodos_obj) == 0:
        filter=""
        if sistem != "all":
            filter = f"sistem eq '{sistem}'"
        # Pure Vector Search
        vector_query = VectorizedQuery(vector=embeddings.embed_query(method), k_nearest_neighbors=10, fields="content_vector", exhaustive=True)
        results = search_client.search(vector_queries= [vector_query],filter=filter,select=["sistem", "content","id"])
        ret_metods_names = []
        ret_metods_sistems = []
        for res in results:
            ret_metods_names.append(res["id"].split("_")[1])
            ret_metods_sistems.append(res["id"].split("_")[0])
        for met in metodos_lista:
            if met.nombre in ret_metods_names:
                indices = [indice for indice, elemento in enumerate(ret_metods_names) if elemento == met.nombre]
                if met.sistema in [ret_metods_sistems[i] for i in indices]:
                    ret_metodos_obj.append(met)
    resp = ""
    for metod in ret_metodos_obj:
        resp +=  method_info_as_string(metod,params_info=True) + "\n"
    return resp


## TOOL 3
@tool("get_all_method_from_sistem", args_schema=sistem)
def get_all_method_from_sistem(sistem: str="all"):
    """ Returns all methods for a given sistem. """

    ret_metodos_obj = []
    for met in metodos_lista:
         if met.sistema.lower().strip() == remover_tildes(sistem.lower().strip()):
            ret_metodos_obj.append(met)


    if len(ret_metodos_obj) == 0:
        resp = "El sistema {sistem} no es parte de Bantotal"
    else:
        resp = ""
        for metod in ret_metodos_obj:
            resp +=  method_info_as_string(metod) + "\n"
            
    return resp




tools = [get_method, get_method_info,get_all_method_from_sistem]
