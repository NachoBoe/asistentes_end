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



# LEVANTAR DATOS


# Levantar base vectorial campos
embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-small")
index_name = "capacitacion3"
credential = AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_API_KEY"))
endpoint = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)




# DEFINIR TOOLS


## TOOL 1: Obtener registros a partir de una descripción

class query_search_engine(BaseModel):
    question: str = Field(description="Question for the engine to search for in the database.")

@tool("bantotal_search_engine",args_schema=query_search_engine)
def bantotal_search_engine(question:str):
    """Searches for information relevant to the question in the database. Returns the top 10 results in relevance order. """
    embedding = embeddings.embed_query(question)
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=30, fields="texto_vector")

    results = search_client.search(  
        search_text=question,  
        vector_queries=[vector_query],
        select=["id", "text","titulo","url","inicio","fin","idx","texto_vector"],
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=10,
    )

    answer = ""

    for result in results:
        answer += f"texto: {result['text']}\n"
        answer += f"Video: {result['titulo']}\n"
        answer += f"url: {result['url']}\n"
        answer += "\n\n"
    return answer


tools = [bantotal_search_engine]
