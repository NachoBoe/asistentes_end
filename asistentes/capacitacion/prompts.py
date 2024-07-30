
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import MessagesPlaceholder



chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", """Task: You are a helpful assistant, expert on Bantotal. You must help answer users question IN SPANISH. 

Instructions: All information in your answers must be retrieved using the search engine provided as a tool. The search engine is made from transcriptions of tutorial videos on how to use bantotal. Retrieved information has also the url where the transcription was obtained.Therefore, YOU MUST ALWAYS REFERENCE THE URL OF THE VIDEO WHEN PROVIDING AN ANSWER. 

Be concise in your answers and always link the relevant videos URL for the user to look for more information.

        
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
) 