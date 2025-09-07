from agents.llm import llm
from langchain_core.output_parsers import StrOutputParser   

# Define the RAG (retrieval-augmented generation) prompt pipeline
from langchain import hub

rag_prompt = hub.pull("rlm/rag-prompt")
rag_chain = rag_prompt | llm | StrOutputParser()