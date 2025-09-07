import os
from pprint import pprint
from pydantic import BaseModel, Field
from langgraph.graph import START, END, StateGraph


from langchain_core.prompts import ChatPromptTemplate

from agents.configs import *
from agents.eam import get_eam_results
from agents.llm import *
from agents.graph_state import GraphState
from agents.question_router import *
from agents.rag_chain import rag_chain
from agents.retrieve import retrieve_and_generate
from agents.measurements import get_database_results

from agents.web_generate import web_and_generate

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


workflow.add_conditional_edges("eam",
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
    result = app.invoke(inputs)

    if "generation" in result:
        pprint(result["generation"])
        pprint(result["datasource"])
        return result["generation"] , result["datasource"]
    else:
        print("No generation found in result")
        return None
