# IMPORTS
from langchain.pydantic_v1 import BaseModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from typing import Optional, Type
from asistentes.src import ConfigurableSearchTool


# INPUTS A LAS TOOLS

## Tool 1
class EmptyInput(BaseModel):
    pass


# TOOLS

## Tool 1
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
    
    
    
# TOOLS

tools = [CustomTool()]
