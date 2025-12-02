from azureopenaimanager.azureopenai_helper import *
from cosmos.cosmosdbmanager import *
from agents.configs import *

def get_reply(user_input, content, 
              conversation_id = None,save_response = True):

    
    cosmosdb_helper = CosmosDBManager(COSMOSDB_ENDPOINT,    
                                    COSMOSDB_KEY, 
                                    COSMOSDB_DATABASE_NAME, 
                                    COSMOSDB_CONTAINER_NAME_CONVERSATIONS)
    
    azure_open_ai_manager = AzureOpenAIManager(
                    endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_API_KEY,
                    deployment_id=AZURE_OPENAI_DEPLOYMENT_ID,
                    api_version="2023-05-15",
                    cosmosdb_helper = cosmosdb_helper
                )             
    
    conversation=[{"role": "system", "content": "If the answer is not found within the context, please mention \
        that the answer is not found \
        Do not answer anything which is not in the context"}]
    reply,conversation_id = azure_open_ai_manager.generate_reply_from_context(user_input, 
                        content,conversation, conversation_id,save_response)
    
    return reply[0]
