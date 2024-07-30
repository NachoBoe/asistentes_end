from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent


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

