from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
from agents.graph_state import GraphState
from agents.rag_chain import rag_chain

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

    return {"question": question, "documents": [web_results_doc], "generation": generation, "datasource": "web_search"}
