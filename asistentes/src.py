# Imports
## Langchain
from langchain.agents import AgentExecutor
from langchain_core.runnables import (
    ConfigurableFieldSpec,
    Runnable,
    RunnableConfig,
)
from langchain_core.runnables.utils import Input, Output
from langchain.tools import BaseTool 
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
## Anotaciones
from typing import Any, AsyncIterator, Dict, List, Optional, cast, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel



# Clase heredada de BaseTool que permite propagar configuraciones a las Tools

class ConfigurableSearchTool(BaseTool, ABC):
    
    # Definir nueva propiedad config para la BaseTool
    config = {}
    
    # Método para agregar configuración a la herramienta
    def with_config(self, config: dict) -> 'ConfigurableSearchTool':
        """Method to configure the tool."""
        self.config = config
        return self
    
    # Propiedades abstractas de la clase BaseTool
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """The description of the tool."""
        pass

    @property
    @abstractmethod
    def args_schema(self) -> Type[BaseModel]:
        """The schema for arguments."""
        pass

    @abstractmethod
    def _run(
        self, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Method to be implemented by subclasses."""
        pass

    @abstractmethod
    async def _arun(
        self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Async method to be implemented by subclasses."""
        pass



# Wrapper de la clase AgentExecutor que permite propagar configuraciones a las herramientas
class CustomAgentExecutor(Runnable):
    """A custom runnable that will be used by the agent executor."""

    # Propiedades de la clase Runnable
    def __init__(self, agent,tools, **kwargs):
        """Initialize the runnable."""
        super().__init__(**kwargs)
        self.agent = agent
        self.tools = tools

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        return self.agent.config_specs
    
    # Metodo Invoke propio de todas las clases Runnable.
    def invoke(self, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        
        # Se levanta el configurable y se propaga a las herramientas
        configurable = cast(Dict[str, Any], config.pop("configurable", {}))
        configured_tools = []
        if configurable:
            for tool in self.tools:
                if issubclass(tool.__class__,ConfigurableSearchTool):
                    configured_tools.append(tool.with_config({"configurable":configurable}))
                else:
                    configured_tools.append(tool)
            configured_agent = self.agent
            # configured_agent = self.agent.with_config({"callbacks":[CostCalcCallbackHandler( "gpt-4o-mini", configurable["usuario"], configurable["asistente"])]})
        else:
            configured_agent = self.agent
            configured_tools = self.tools
        
        # Se define el AgentExecutor pero con las herramientas configuradas
        executor = AgentExecutor(
            agent=configured_agent,
            tools=configured_tools,
        ).with_config({"run_name": "executor"})
        
        # Se ejecuta el método invoke del AgentExecutor modificado
        ans = executor.invoke(input, config=config)
        return ans
    
    # Metodo asincrono astream propio de todas las clases Runnable.
    async def astream(self,input: Input,config: Optional[RunnableConfig] = None,**kwargs: Optional[Any]) -> AsyncIterator[Output]:

        # Se levanta el configurable y se propaga a las herramientas
        configurable = cast(Dict[str, Any], config.pop("configurable", {}))
        configured_tools = []
        if configurable:
            for tool in self.tools:
                if issubclass(tool.__class__,ConfigurableSearchTool):
                    configured_tools.append(tool.with_config({"configurable":configurable}))
                else:
                    configured_tools.append(tool)
            configured_agent = self.agent
            # configured_agent = self.agent.with_config({"callbacks":[CostCalcCallbackHandler( "gpt-4o-mini", configurable["usuario"], configurable["asistente"])]})
        else:
            configured_agent = self.agent
            configured_tools = self.tools
        
        # Se define el AgentExecutor pero con las herramientas configuradas        
        executor = AgentExecutor(
            agent=configured_agent,
            tools=configured_tools,
        ).with_config({"run_name": "executor"})
        
        # Se ejecuta el método astream del AgentExecutor modificado
        async for output in executor.astream(input, config=config, **kwargs):
            yield output    



## CLASE PARA CALCULAR COSTOS (FALTA IMPLEMENTAR PARTES)

# class CostCalcCallbackHandler(AsyncCallbackHandler):
#     def __init__(self, model_name, usuario,asistente, *args, **kwargs):
#         self.model_name = model_name
#         self.encoding = tiktoken.encoding_for_model(model_name)
#         self.endpoint = "http://127.0.0.1:8001/add_trace"
#         self.usuario = usuario
#         self.asistente = asistente
#         super().__init__(*args, **kwargs)

#     async def on_llm_start(
#         self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
#     ) -> None:
#         for prompt in prompts:
#             self.trace_prompt_tokens(len(self.encoding.encode(prompt)))

#     async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
#         for generation_list in response.generations:
#             for generation in generation_list:
#                 self.trace_completion_tokens(len(self.encoding.encode(generation.text)))

#     def trace_prompt_tokens(self, prompt_tokens):
#         trace_data = {
#             "asistente": self.asistente,
#             "usuario": self.usuario,
#             "date": datetime.now().isoformat(),
#             "tokens_in": prompt_tokens,
#             "tokens_out": 0
#         }
#         response = requests.post(self.endpoint, json=trace_data)


#     def trace_completion_tokens(self, completion_tokens):
#         trace_data = {
#             "asistente": self.asistente,
#             "usuario": self.usuario,
#             "date": datetime.now().isoformat(),
#             "tokens_in": 0,
#             "tokens_out": completion_tokens
#         }
#         response = requests.post(self.endpoint, json=trace_data)

