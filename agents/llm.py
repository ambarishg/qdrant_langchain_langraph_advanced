import os

from agents.configs import AZURE_OPENAI_DEPLOYMENT_ID


DEFAULT_CHAT_MODEL = "azure_openai:gpt-4o"
DEFAULT_METADATA = "CRAG, gpt4o"


def initialize_llm():
    """
    Initialize the LLM model used for chat.
    Configuration is loaded from environment variables to support
    different model providers and deployment names across environments.
    """
    from langchain.chat_models import init_chat_model

    chat_model = os.getenv("LANGCHAIN_CHAT_MODEL", DEFAULT_CHAT_MODEL)
    azure_deployment = os.getenv(
        "LANGCHAIN_AZURE_OPENAI_DEPLOYMENT",
        AZURE_OPENAI_DEPLOYMENT_ID,
    )
    metadata = os.getenv("LLM_METADATA", DEFAULT_METADATA)

    llm_kwargs = {}
    if azure_deployment:
        llm_kwargs["azure_deployment"] = azure_deployment

    llm = init_chat_model(chat_model, **llm_kwargs)
    return llm, metadata


llm, metadata = initialize_llm()
