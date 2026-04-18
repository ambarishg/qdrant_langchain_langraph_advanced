# Define TypedDict for graph state
from typing import Any, TypedDict


class GraphState(TypedDict):
    token:str
    question: str
    generation: Any
    documents: Any
    datasource: str
