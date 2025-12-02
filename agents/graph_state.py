# Define TypedDict for graph state
from typing import List, TypedDict
class GraphState(TypedDict):
    token:str
    question: str
    generation: str
    documents: List[str]
    datasource: str