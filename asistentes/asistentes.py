from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent


from langchain_core.runnables import (
    ConfigurableField,
    ConfigurableFieldSpec,
    Runnable,
    RunnableConfig,
)
from langchain_core.utils.function_calling import format_tool_to_openai_function
from typing import Any, AsyncIterator, Dict, List, Optional, cast
from langchain_core.runnables.utils import Input, Output


class CustomAgentExecutor(Runnable):
    """A custom runnable that will be used by the agent executor."""

    def __init__(self, agent,tools, **kwargs):
        """Initialize the runnable."""
        super().__init__(**kwargs)
        self.agent = agent
        self.tools = tools

    def invoke(self, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        """Will not be used."""
        configurable = cast(Dict[str, Any], config.pop("configurable", {}))
        configured_tools = []
        if configurable:
            for tool in self.tools:
                configured_tools.append(tool.with_config({"configurable":configurable}))
        executor = AgentExecutor(
            agent=self.agent,
            tools=configured_tools,
        ).with_config({"run_name": "executor"})

        return executor.invoke(input, config=config)

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        return self.agent.config_specs

    async def astream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        """Stream the agent's output."""
        configurable = cast(Dict[str, Any], config.pop("configurable", {}))
        configured_tools = []
        if configurable:
            for tool in self.tools:
                configured_tools.append(tool.with_config({"configurable":configurable}))
        executor = AgentExecutor(
            agent=self.agent,
            tools=configured_tools,
        ).with_config({"run_name": "executor"})

        async for output in executor.astream(input, config=config, **kwargs):
            yield output

# API
import asistentes.API.tools as t_api
import asistentes.API.prompts as p_api

openai_api = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_api = create_openai_tools_agent(openai_api, t_api.tools, p_api.chat_template)
asistente_api = AgentExecutor(agent=agent_api, tools=t_api.tools, verbose=False)



# CORE
import asistentes.CORE.tools as t_core
import asistentes.CORE.prompts as p_core

openai_core = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_core = create_openai_tools_agent(openai_core, t_core.tools, p_core.chat_template)
asistente_core = AgentExecutor(agent=agent_core, tools=t_core.tools, verbose=False)


# migracion
import asistentes.migracion.tools as t_migracion
import asistentes.migracion.prompts as p_migracion

openai_migracion = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_migracion = create_openai_tools_agent(openai_migracion, t_migracion.tools, p_migracion.chat_template)
asistente_migracion = AgentExecutor(agent=agent_migracion, tools=t_migracion.tools, verbose=False)


# capacitacion
import asistentes.capacitacion.tools as t_capacitacion
import asistentes.capacitacion.prompts as p_capacitacion

openai_capacitacion = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_capacitacion = create_openai_tools_agent(openai_capacitacion, t_capacitacion.tools, p_capacitacion.chat_template)
asistente_capacitacion = AgentExecutor(agent=agent_capacitacion, tools=t_capacitacion.tools, verbose=False)

# pseudoCode
import asistentes.pseudoCode.tools as t_pseudoCode
import asistentes.pseudoCode.prompts as p_pseudoCode

openai_pseudoCode = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_pseudoCode = create_openai_tools_agent(openai_pseudoCode, t_pseudoCode.tools, p_pseudoCode.chat_template)
asistente_pseudoCode = AgentExecutor(agent=agent_pseudoCode, tools=t_pseudoCode.tools, verbose=False)

# requerimientos
import asistentes.requerimientos.tools as t_requerimientos
import asistentes.requerimientos.prompts as p_requerimientos

openai_requerimientos = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_requerimientos = create_openai_tools_agent(openai_requerimientos, t_requerimientos.tools, p_requerimientos.chat_template)
asistente_requerimientos = CustomAgentExecutor(agent=agent_requerimientos, tools=t_requerimientos.tools)
