from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from agents.graph_state import GraphState
from agents.llm import llm


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