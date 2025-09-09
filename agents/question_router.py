from agents.graph_state import GraphState
from pydantic import field_validator
from pydantic import BaseModel, Field
from typing import Literal
from agents.llm import llm
from langchain_core.prompts import ChatPromptTemplate

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["voltage", "web_search", "measurements","EAM"] = Field(
        ...,
        description="""
        
        Given a user question choose to route it to 
        transformer store or web search."""
    )

    # Validator to ensure datasource is one of the specified options
    @field_validator('datasource')
    def validate_datasource(cls, v):
        if v not in ["voltage", "web_search", "measurements","EAM"]:
            raise ValueError("Invalid datasource. Must be 'voltage', 'web_search', 'measurements' or 'EAM'.")
        return v


structured_llm_router = llm.with_structured_output(RouteQuery)

# Prompt
# Prompt
system = """
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

If the query is about:  
- Assets, work orders, locations, hazards → EAM 
- Measurements or historical data → measurements  
- Medium voltage, roadways, or electrical concepts/formulas → voltage  
- Current events, news, or general knowledge → web_search

"""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router

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
        source = question_router.invoke({"question": question})
        print(f"Routed to: {source.datasource}")
        if source.datasource == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "web_search"
        elif source.datasource == "voltage":
            print("---ROUTE QUESTION TO RAG---")
            return "voltage"
        elif source.datasource == "measurements":
            print("---ROUTE QUESTION TO MEASUREMENTS---")
            return "measurements"
        elif source.datasource == "EAM":
            print("---ROUTE QUESTION TO EAM---")
            return "eam"
    except Exception as e:
        print(f"Error in route_question: {e}")
        return "web_search"
