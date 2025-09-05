import os

from dotenv import load_dotenv
# Load environment variables for secrets
load_dotenv(".env")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_KEY")
COLLECTION_NAME = "PWD_SENTENCE_TRANSFORMERS"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")