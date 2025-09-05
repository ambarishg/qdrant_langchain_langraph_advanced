import os
from typing import List
from typing_extensions import TypedDict
from pprint import pprint

from pydantic import BaseModel, Field
from IPython.display import display

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain.schema import Document
from langgraph.graph import START, END, StateGraph
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.prompts import ChatPromptTemplate
from langchain.document_loaders import HuggingFaceDatasetLoader
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from typing import Literal

from agents.configs import *
from agents.generate_sql import get_sql_query
from agents.eam import get_eam_results

def initialize_llm():
    """
    Initialize the LLM model used for chat.
    You can replace the model with different providers or configurations as needed.
    """
    from langchain.chat_models import init_chat_model

    llm = init_chat_model(
        "azure_openai:gpt-4o",
        azure_deployment="gpt4o",
    )
    metadata = "CRAG, gpt4o"
    return llm, metadata


llm, metadata = initialize_llm()



# Initialize embeddings and vector store retriever
embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False},
)

qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

retriever = qdrant.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)


# Define the RAG (retrieval-augmented generation) prompt pipeline
from langchain import hub

rag_prompt = hub.pull("rlm/rag-prompt")
rag_chain = rag_prompt | llm | StrOutputParser()


def format_documents(docs: List[Document]) -> str:
    """Concatenate page contents of documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


# Define TypedDict for graph state
class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]


def retrieve_and_generate(state: GraphState) -> GraphState:
    """Retrieve documents from Voltage vector store and generate an answer."""
    print("---RETRIEVE AND GENERATE---")
    question = state["question"]

    docs = retriever.invoke(question)
    documents_text = "\n".join([d.page_content for d in docs])

    generation = rag_chain.invoke({"context": documents_text, "question": question})

    return {"question": question, "documents": documents_text, "generation": generation}


# Setup web search tool
web_search_tool = TavilySearchResults(k=3)


def web_and_generate(state: GraphState) -> GraphState:
    """Perform web search and generate an answer."""
    print("---WEB SEARCH AND GENERATE---")
    question = state["question"]

    search_results = web_search_tool.invoke({"query": question})
    combined_content = "\n".join([result["content"] for result in search_results])
    web_results_doc = Document(page_content=combined_content)

    generation = rag_chain.invoke({"context": [web_results_doc], "question": question})

    return {"question": question, "documents": [web_results_doc], "generation": generation}


# Define answer grading model and prompt
class GradeAnswer(BaseModel):
    """Binary score assessing if the answer addresses the question."""
    binary_score: str = Field(description="Answer addresses the question: 'yes' or 'no'")


grading_system_prompt = (
    "You are a grader assessing whether an answer resolves a question.\n"
    "Give a binary score 'yes' or 'no'.\n"
    "'No' means the answer does not resolve the question.\n"
    "'Yes' means the answer resolves the question."
)

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", grading_system_prompt),
    ("human", "User question:\n\n{question}\n\nLLM generation:\n{generation}"),
])

structured_llm_grader = llm.with_structured_output(GradeAnswer)
answer_grader = answer_prompt | structured_llm_grader




def grade_answer(state: GraphState) -> str:
    """Evaluate the quality of the generated answer."""
    print("---GRADE ANSWER---")
    question = state["question"]
    generation = state["generation"]

    grade = answer_grader.invoke({"question": question, "generation": generation})
    print(f"Grade: {grade.binary_score}")

    return grade.binary_score


def get_database_results(state: GraphState) -> dict:
    """Extract and return measurements from the state."""

    print("---GET MEASUREMENTS---")
    try:

        question, sql_query = get_sql_query(state)
        
        from db.duckdb.duckdbhelper import DuckDBDatabaseHelper
        duckdb_helper = DuckDBDatabaseHelper('data/test_duckdb.db')
        duckdb_helper.connect()
        results, column_names = duckdb_helper.fetch_all(sql_query)
        duckdb_helper.close_connection()

        if results is not None and len(results) > 0:
            import pandas as pd
            df = pd.DataFrame(results)
            df.columns = column_names
            dict_df = df.to_dict(orient='records')
            return {"question": question, "generation": dict_df, "documents": str(sql_query)}
        else:
            return {"question": question, "generation": [{'0':'No records found'}], "documents": str(sql_query)}
    except Exception as e:
        print(f"Error in get_measurements: {e}")
        return {"question": question, "generation": [{'0':'No records found'}], "documents": str(sql_query)}


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["voltage", "web_search", "measurements","EAM"] = Field(
        ...,
        description="""
        
        Given a user question choose to route it to 
        transformer store or web search."""
    )


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

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
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


from langgraph.graph import END, StateGraph, START

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("web_search", web_and_generate)  # web search
workflow.add_node("voltage", retrieve_and_generate)  # retrieve
workflow.add_node("measurements", get_database_results)  # measurements
workflow.add_node("eam", get_eam_results)  # eam

workflow.add_conditional_edges(START, route_question,
                               {"web_search": "web_search",
                                "voltage": "voltage",
                                "measurements": "measurements",
                                "eam": "eam"
                                })



workflow.add_conditional_edges("voltage",
                                grade_answer, 
                                {"yes": END, 
                                 "no": "web_search"
                                 })
workflow.add_edge("web_search", END)
workflow.add_edge("measurements", END)
workflow.add_edge("eam", END)

# Compile the state graph application
app = workflow.compile()


def run_app(question: str) -> str:
    """
    Run the QA application on the input question.
    Returns the generated answer or None if unavailable.
    """
    inputs = {"question": question}
    result = app.invoke(inputs)

    if "generation" in result:
        pprint(result["generation"])
        return result["generation"]
    else:
        print("No generation found in result")
        return None
