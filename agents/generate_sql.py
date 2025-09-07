from agents.configs import *

def get_sql_query(state, context=""):
    question = state["question"]

    from azureopenaimanager.azureopenai_helper import AzureOpenAIManager

    azure_open_ai_manager = AzureOpenAIManager(
                        endpoint=AZURE_OPENAI_ENDPOINT,
                        api_key=AZURE_OPENAI_API_KEY,
                        deployment_id=AZURE_OPENAI_DEPLOYMENT_ID,
                        api_version=OPENAI_API_VERSION
                    )
    
    sql_query = None
    dict_df = None
    print(f"Context: {context}")
    if context == "":
        msg,_,_,_ = azure_open_ai_manager.generate_answer_document(question)
    else:
        msg,_,_,_ = azure_open_ai_manager.generate_answer_document_with_context(question,context)

    if "```sql" not in msg:
        sql_query = None
    else:
        query = msg.split("```sql")[1].split("```")[0].strip().replace("\n", " ")
        sql_query = query
    
    print(f"SQL Query: {sql_query}")
    return question,sql_query
