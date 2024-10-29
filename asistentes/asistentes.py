# Imports
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent
from asistentes.src import CustomAgentExecutor


# API
import asistentes.API.tools as t_api
import asistentes.API.prompts as p_api

openai_api = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_api = create_openai_tools_agent(openai_api, t_api.tools, p_api.chat_template)
asistente_api = CustomAgentExecutor(agent=agent_api, tools=t_api.tools)



# CORE
import asistentes.CORE.tools as t_core
import asistentes.CORE.prompts as p_core

openai_core = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_core = create_openai_tools_agent(openai_core, t_core.tools, p_core.chat_template)
asistente_core = CustomAgentExecutor(agent=agent_core, tools=t_core.tools)


# migracion
import asistentes.migracion.tools as t_migracion
import asistentes.migracion.prompts as p_migracion

openai_migracion = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_migracion = create_openai_tools_agent(openai_migracion, t_migracion.tools, p_migracion.chat_template)
asistente_migracion = CustomAgentExecutor(agent=agent_migracion, tools=t_migracion.tools)


# capacitacion
import asistentes.capacitacion.tools as t_capacitacion
import asistentes.capacitacion.prompts as p_capacitacion

openai_capacitacion = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_capacitacion = create_openai_tools_agent(openai_capacitacion, t_capacitacion.tools, p_capacitacion.chat_template)
asistente_capacitacion = CustomAgentExecutor(agent=agent_capacitacion, tools=t_capacitacion.tools)

# pseudoCode
import asistentes.pseudoCode.tools as t_pseudoCode
import asistentes.pseudoCode.prompts as p_pseudoCode

openai_pseudoCode = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_pseudoCode = create_openai_tools_agent(openai_pseudoCode, t_pseudoCode.tools, p_pseudoCode.chat_template)
asistente_pseudoCode = CustomAgentExecutor(agent=agent_pseudoCode, tools=t_pseudoCode.tools)

# requerimientos
import asistentes.requerimientos.tools as t_requerimientos
import asistentes.requerimientos.prompts as p_requerimientos

openai_requerimientos = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_requerimientos = create_openai_tools_agent(openai_requerimientos, t_requerimientos.tools, p_requerimientos.chat_template)
asistente_requerimientos = CustomAgentExecutor(agent=agent_requerimientos, tools=t_requerimientos.tools)

# instalador
import asistentes.instalador.tools as t_instalador
import asistentes.instalador.prompts as p_instalador

openai_instalador = ChatOpenAI(model="gpt-4o-mini",temperature=0.0,streaming=True)
agent_instalador = create_openai_tools_agent(openai_instalador, t_instalador.tools, p_instalador.chat_template)
asistente_instalador = CustomAgentExecutor(agent=agent_instalador, tools=t_instalador.tools)