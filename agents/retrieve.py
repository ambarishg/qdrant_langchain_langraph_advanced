from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_qdrant import QdrantVectorStore


from agents.configs import *
from agents.llm import *
from agents.graph_state import GraphState
from typing import List
from typing_extensions import TypedDict
from agents.rag_chain import rag_chain


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


def format_documents(docs: List[Document]) -> str:
    """Concatenate page contents of documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


def retrieve_and_generate(state: GraphState) -> GraphState:
    """Retrieve documents from Voltage vector store and generate an answer."""
    print("---RETRIEVE AND GENERATE---")
    question = state["question"]

    docs = retriever.invoke(question)
    documents_text = "\n".join([d.page_content for d in docs])

    generation = rag_chain.invoke({"context": documents_text, "question": question})

    return {"question": question, "documents": documents_text, "generation": generation ,"datasource": "voltage"}

