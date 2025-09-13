import os
from pprint import pprint
from langgraph.graph import START, END, StateGraph


from agents.eam import get_eam_results
from agents.llm import *
from agents.graph_state import GraphState
from agents.question_router_with_memory import *
from agents.retrieve import retrieve_and_generate
from agents.measurements import get_database_results
from agents.web_generate import web_and_generate
from agents.grade_answer import grade_answer

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


workflow.add_conditional_edges("eam",
                                grade_answer, 
                                {"yes": END, 
                                 "no": "web_search"
                                 })

workflow.add_conditional_edges("measurements",
                                grade_answer, 
                                {"yes": END, 
                                 "no": "web_search"
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

def get_eam_workflow():
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("web_search", web_and_generate)  # web searchements
    workflow.add_node("eam", get_eam_results)  # eam

    workflow.add_edge(START,"eam")

    workflow.add_conditional_edges("eam",
                                    grade_answer, 
                                    {"yes": END, 
                                    "no": "web_search"
                                    })

    

    workflow.add_edge("web_search", END)



    # Compile the state graph application
    app = workflow.compile()

    return app

def get_measurements_workflow():
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("measurements", get_database_results)
    workflow.add_node("web_search", web_and_generate)  # web searchements

    workflow.add_edge(START,"measurements")

    workflow.add_conditional_edges("measurements",
                                    grade_answer, 
                                    {"yes": END, 
                                    "no": "web_search"
                                    })

    

    workflow.add_edge("web_search", END)



    # Compile the state graph application
    app = workflow.compile()

    return app

def run_app(question: str, token:str) -> str:
    """
    Run the QA application on the input question.
    Returns the generated answer or None if unavailable.
    """
    inputs = {"question": question,"token":token}

    print(inputs)

    result = app.invoke(inputs)

    if "generation" in result:
        pprint(result["generation"])
        pprint(result["datasource"])
        return result["generation"] , result["datasource"]
    else:
        print("No generation found in result")
        return "No result found" , "No data source"

def run_eam_app(question: str, token:str) -> str:
    """
    Run the QA application on the input question.
    Returns the generated answer or None if unavailable.
    """
    inputs = {"question": question,"token":token}

    print(inputs)

    eam_app = get_eam_workflow()

    result = eam_app.invoke(inputs)

    if "generation" in result:
        pprint(result["generation"])
        pprint(result["datasource"])
        return result["generation"] , result["datasource"]
    else:
        print("No generation found in result")
        return "No result found" , "No data source"

def run_measurements_app(question: str, token:str) -> str:
    """
    Run the QA application on the input question.
    Returns the generated answer or None if unavailable.
    """
    inputs = {"question": question,"token":token}

    print(inputs)

    measurements_app = get_measurements_workflow()

    result = measurements_app.invoke(inputs)

    if "generation" in result:
        pprint(result["generation"])
        pprint(result["datasource"])
        return result["generation"] , result["datasource"]
    else:
        print("No generation found in result")
        return "No result found" , "No data source"