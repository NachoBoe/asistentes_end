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

embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large")
index_name = "instalador"
credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_API_KEY"])
endpoint = "https://bantotalsearchai.search.windows.net"
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)




# FUNCIONES AUXILIARES

def remover_tildes(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')




# DEFINIR TOOLS

class Query(BaseModel):
    query: str = Field(description="Query to search in the engine.")


@tool("system_informaton", args_schema=Query)
def system_informaton(query:str):
    """Bantotal Semantic Search engine that retrieves relevant information from Bantotal System."""

    embedding = embeddings.embed_query(query)
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields="embedding", exhaustive=True)
    results = search_client.search(  
        search_text=query,  
        vector_queries=[vector_query],
        select=["id", "content","section", "path","system"],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=5,
    )

    ans = ""
    results_record = []
    for result in results:
        print(result["path"] + " - " + str(result["@search.reranker_score"]))
        results_record.append(result)
    
    retrieved_sections = [x["section"] for x in results_record]
    
    for result in results_record:
        sec = result["section"]
        if not any([sec.startswith(x) and x!=sec for x in retrieved_sections]):
            ans += f"Manual: MDI - {(result['system']).replace('_','' '').upper()} \n"
            ans += f"Sección: {result['path']} \n"
            ans += f"Contenido: \n{result['content']} \n"
            ans += "\n\n"
    return ans


tools = [system_informaton]
