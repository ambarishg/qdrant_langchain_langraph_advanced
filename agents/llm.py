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