from agents.graph_state import GraphState
from pydantic import field_validator
from pydantic import BaseModel, Field
from typing import Literal
from agents.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from agents.generate_reply import get_reply


# Prompt
# Prompt
system_prompt = """
You are an expert router that decides the most relevant datasource to answer a user’s question. 
The possible datasources are:

1. EAM 
   - Contains: work orders, assets, locations, hazards, hazard locations, and control measures.

2. measurements 
   - Contains: current and historical measurement data (numerical, time-series, sensor readings, etc.).

3. voltage
   - Contains: information related to medium voltage, roadways, and electrical engineering (including equations, formulas, and technical concepts).

4. web search
   - Contains: information about current events, news, and general knowledge outside of the above systems.

Your task:
For every user question, determine which single datasource is most appropriate to answer it.  
Select only the datasource that contains the most relevant information needed.  
Do not use multiple sources—choose the best one.

For measurements, the data source is always measurements

If the query is about:  
- Assets, work orders, locations, hazards → EAM 
- Measurements or historical data → measurements  
- Medium voltage, roadways, or electrical concepts/formulas → voltage  
- Current events, news, or general knowledge → web_search

Ensure the data sources must be one of the listed below
EAM
measurements
voltage
web_search

"""


def get_question_router(question,conversation_id):
    reply = get_reply(question,system_prompt,conversation_id)
    print(reply)
    return reply

def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    try:
        print("---ROUTE QUESTION---")
        question = state["question"]
        conversation_id = state["token"]
        source = get_question_router(question,conversation_id)
        print(f"Routed to: {source}")
        if source == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "web_search"
        elif source == "voltage":
            print("---ROUTE QUESTION TO RAG---")
            return "voltage"
        elif source == "measurements":
            print("---ROUTE QUESTION TO MEASUREMENTS---")
            return "measurements"
        elif source == "EAM":
            print("---ROUTE QUESTION TO EAM---")
            return "eam"
        else:
            return "web_search"
    except Exception as e:
        print(f"Error in route_question: {e}")
        return "web_search"
