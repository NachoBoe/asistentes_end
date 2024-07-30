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


# Levantar manuales
path = "./asistentes/migracion/data/Manuales_migracion/"
manuales = []
for filename in os.listdir(path):
    with open(path + filename, 'rb') as file:
        manuales.append(dill.load(file))
for m in manuales:
    if m.title == "Manual Proceso de Migracion":
        manual_general = m

# Levantar bandejas
with open("./asistentes/migracion/data/manuales_object.pkl", 'rb') as f:
    manulales = dill.load(f)
with open('./asistentes/migracion/data/bandejas.dill', 'rb') as file:
    bandejas = dill.load(file)



# Levantar base vectorial campos
embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002")
index_name = "migracion_campos"
credential = AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_API_KEY"))
endpoint = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
sc_campo = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)



# FUNCIONES AUXILIARES
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def remover_tildes(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')





# DEFINIR TOOLS


## TOOL 1: Obtener registros a partir de una descripción

class desc_campo(BaseModel):
    information: str = Field(description="Information that wants to be stored in a record.")
    system = str = Field(description="Filter the search to a particular system. The possible systems are: ['Cuentas Vistas', 'Cuentas y Personas', 'Chequeras', 'Depósitos', 'Microfinanzas', 'Saldos Iniciales', 'Facultades', 'Líneas de Crédito','Garantías', 'Préstamos', 'Acuerdos de Sobregiro', 'Tarjetas de Débito', 'Descuentos', 'all']", default="all")

@tool("retrieve_records_from_description",args_schema=desc_campo)
def retrieve_records_from_description(information:str, system:str="all"):
    """Migrating to Bantotal requieres the user to fill in a lot of records. This tool helps you find the records that are related to the information you have."""
    embedding = embeddings.embed_query(information)
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=20, fields="content_vector", exhaustive=True)

    if system != "all":
        filter=f"manual eq 'Manual {system}'"
    else:
        filter=None

    results = sc_campo.search(  
        vector_queries= [vector_query],
        filter=filter,
        select=["content","manual", "campo", "bandeja", "tipo"],
    )

    string = ""
    bdjs = []
    for md in results:
        string += f'{{ "Campo": "{md["campo"]}", "Descripción": "{md["content"]}",  "Bandeja/Tabla": "{md["bandeja"]}", "Tipo": "{md["tipo"]}", "Sistema": {md["manual"].replace("Manual ", "")} }} \n\n'
        if md["bandeja"] not in bdjs:
            bdjs.append(md["bandeja"])
    tray_string = f"Trays: \n"
    for manual in manulales:
        for bandeja in manulales[manual].bandejas:
            if bandeja.codigo in bdjs:
                tray_string += f'{{ "Bandeja/Tabla": "{bandeja.codigo}", "Descripción": "{bandeja.descripcion}", "Sistema": "{manual.replace("Manual ", "")}" }} \n\n'
    return tray_string + "\n\n Suitable Fields: \n"+string



# TOOL 2: Obtener información de un sistema en particular
class system_retriever_input(BaseModel):
    system: str = Field(description="System to retrieve information from. The possible systems are: ['Cuentas Vistas', 'Cuentas y Personas', 'Chequeras', 'Depósitos', 'Microfinanzas', 'Saldos Iniciales', 'Facultades', 'Líneas de Crédito','Garantías', 'Préstamos', 'Acuerdos de Sobregiro', 'Tarjetas de Débito', 'Descuentos']")



@tool("retrieve_sistem_migration_information",args_schema=system_retriever_input)
def retrieve_sistem_migration_information(system:str):
    """ Retrieves content relevant to the migration of a particular sistem. The content details about elements such as the trays (without the fields), the control and dump programs, the transactions, previous requierements, code errors. It also provides a conceptual guide on how to migrate the system, but not how to actually execute it in Bantotal. """
    total_token = 0
    content = ""
    print(remover_tildes(system.lower()))
    for m in manuales:
        print(m.title.lower())
        if m.title.lower() == "manual " + remover_tildes(system.lower()):
            manual = m
            break
    
    retrieved_secs_filt = ["1", "3"]

    for s in retrieved_secs_filt:
        new_sect = manual.get_section(s)
        token = len(encoding.encode(new_sect))
        print(token)
        if token + total_token < 11000:
            content += new_sect + "\n\n"
            total_token += token
        else:
            print("Section {s} was not included in the answer because it exceeded the token limit")
    return content


# TOOL 3: Obtener información del proceso de migración
class general_retriever_input(BaseModel):
    retrieve_sec_1: bool = Field(description="Retrieve an overview of how the migration process works. ", default=False)
    retrieve_sec_2: bool = Field(description="Retrieve a detailed guide on how to execute the migration for a sistem. , such as create trays, execute control/dump programs, paralelize or use sql sentences, among other.", default=False)
    retrieve_sec_3: bool = Field(description="Retrieve detailed information of the parameters that customize the migration process.", default=False)



@tool("retrieve_migration_process_information",args_schema=general_retriever_input)
def retrieve_migration_process_information(retrieve_sec_1: bool = False, retrieve_sec_2: bool = False, retrieve_sec_3: bool = False):
    """Retrieves information relevant to the migration process and the execution of the migration for a sistem. The informations is grouped in three setions.  """
    total_token = 0
    content = ""

    
    retrieved_secs_filt = []
    if retrieve_sec_1:
        retrieved_secs_filt.append("3")
    if retrieve_sec_2:
        retrieved_secs_filt.append("2")
    if retrieve_sec_3:
        retrieved_secs_filt.append("4")

    for s in retrieved_secs_filt:
        new_sect = manual_general.get_section(s)
        token = len(encoding.encode(new_sect))
        print(token)
        if token + total_token < 11000:
            content += new_sect + "\n\n"
            total_token += token
        else:
            print("Section {s} was not included in the answer because it exceeded the token limit")
    return content




# TOOL 4: Obtener campos de una bandeja
class tray_retriever_input(BaseModel):
    tray: str = Field(description="Tray that wants to be retrieved the fields from.")
    system: str = Field(description="System the tray belongs to. The possible systems are: ['Cuentas Vistas', 'Cuentas y Personas', 'Chequeras', 'Depósitos', 'Microfinanzas', 'Saldos Iniciales', 'Facultades', 'Líneas de Crédito','Garantías', 'Préstamos', 'Acuerdos de Sobregiro', 'Tarjetas de Débito', 'Descuentos']", default="all")



@tool("retrieve_fields_from_tray",args_schema=tray_retriever_input)
def retrieve_fields_from_tray(tray:str, system:str="all"):
    """Retrieves the fields from a tray with a brief description of each."""
    total_token = 0
    content = ""
    tray = tray.upper()
    if system != "all":
        system = "Manual " + remover_tildes(system)
        try:
            content += f"Bandeja: {tray}\n Descripcion:{str(bandejas[system][tray]['descripcion'])} \n Registros: {str(bandejas[system][tray]['registros'])}\n"
        except:
            content += "No se encontraron registros para la bandeja solicitada"
    else:
        for s in bandejas:
            try:
                content += f"Bandeja: {tray}\n Sistema:{s} \n Descripcion:{str(bandejas[s][tray]['descripcion'])} \n Campos:\n {str(bandejas[s][tray]['registros'])}\n"
            except:
                continue
    return content


# DEFINIR AGENTE
tools = [retrieve_migration_process_information, retrieve_sistem_migration_information, retrieve_fields_from_tray, retrieve_records_from_description]
