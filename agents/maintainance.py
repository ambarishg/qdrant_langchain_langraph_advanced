import os
from pprint import pprint
from langgraph.graph import START, END, StateGraph


from agents.eam import get_eam_results
from agents.llm import *
from agents.graph_state import GraphState
from agents.question_router import *
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


def run_app(question: str) -> str:
    """
    Run the QA application on the input question.
    Returns the generated answer or None if unavailable.
    """
    inputs = {"question": question}

    config = {"configurable": {"thread_id": "1"}}
    result = app.invoke(inputs,config = config)

    if "generation" in result:
        pprint(result["generation"])
        pprint(result["datasource"])
        return result["generation"] , result["datasource"]
    else:
        print("No generation found in result")
        return "No result found" , "No data source"
