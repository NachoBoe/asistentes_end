# IMPORTS

from langchain.tools import tool


# DEFINIR TOOLS

@tool("empty_tool")
def empty_tool():
    """Empty tool. Do not use. Answer directly according to the system prompt."""
    return None

tools = [empty_tool]
