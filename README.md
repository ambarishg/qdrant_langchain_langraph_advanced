# Qdrant + LangChain + LangGraph Advanced

This project exposes a FastAPI application that answers user questions by routing them through a LangGraph workflow. Depending on the query, the system can:

- retrieve medium-voltage knowledge from a Qdrant vector store,
- generate and execute SQL against local DuckDB datasets for measurements and EAM data,
- fall back to Tavily web search for general or current-information queries,
- generate final responses with Azure OpenAI while preserving short conversation history in Cosmos DB.

## What the application does

The API accepts a natural-language question and an `Authorization` bearer token. Internally, a router classifies the question into one of four data sources:

- `voltage`: semantic retrieval from Qdrant using `sentence-transformers/all-MiniLM-L6-v2`
- `measurements`: SQL generation over `data/test_duckdb.db`
- `EAM`: SQL generation over `data/eam.db`
- `web_search`: Tavily search for information outside the local knowledge sources

The main workflow is defined in `agents/maintainance.py` and exposed by `app.py`.

## Project structure

- `app.py`: FastAPI entry point
- `agents/`: LangGraph workflow, routing, retrieval, SQL generation, and response generation
- `azureopenaimanager/`: Azure OpenAI wrapper and prompts
- `cosmos/`: Cosmos DB helper used for conversation persistence
- `db/`: database helpers for DuckDB, SQLite, and MySQL
- `data/`: local DuckDB files used by the measurements and EAM flows
- `notebooks/`: setup notebooks, including Qdrant collection creation
- `docs/`: example questions and notes

## Prerequisites

You need the following before running the API:

- Python 3.10 or newer
- Access to an Azure OpenAI resource and deployed chat model
- A Qdrant instance with the required collection populated
- A Tavily API key for web search
- An Azure Cosmos DB account and container for conversation storage

The code expects the local DuckDB files to exist:

- `data/test_duckdb.db`
- `data/eam.db`

These files are already present in the repository.

## Installation

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root. The repository includes `.env.sample`, but the running application needs additional variables beyond that sample.

Use this as a working template:

```env
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
OPENAI_API_VERSION="2025-03-01-preview"
LANGCHAIN_CHAT_MODEL="azure_openai:gpt-4o"
LANGCHAIN_AZURE_OPENAI_DEPLOYMENT="gpt-4o"
LLM_METADATA="CRAG, gpt4o"

TAVILY_API_KEY=""

QDRANT_URL=""
QDRANT_KEY=""

COSMOSDB_ENDPOINT=""
COSMOSDB_KEY=""
COSMOSDB_DATABASE_NAME=""
COSMOSDB_CONTAINER_NAME_CONVERSATIONS=""
COSMOSDB_CONTAINER_NAME_CONVERSATIONS_HEADER=""
COSMOSDB_CONTAINER_NAME_CATEGORY=""
```

Notes:

- `AZURE_OPENAI_DEPLOYMENT_NAME` must match the Azure OpenAI deployment you want to use.
- `agents/llm.py` now reads the LangChain model from `LANGCHAIN_CHAT_MODEL` and the deployment from `LANGCHAIN_AZURE_OPENAI_DEPLOYMENT`, falling back to `AZURE_OPENAI_DEPLOYMENT_NAME` when the LangChain-specific deployment variable is not set.
- `LLM_METADATA` controls the metadata label returned by `agents/llm.py`.
- The Qdrant collection name is currently fixed in `agents/configs.py` as `PWD_SENTENCE_TRANSFORMERS`.
- Tavily is used by `agents/web_generate.py`.
- Cosmos DB is used by `agents/generate_reply.py` to persist conversation history keyed by the bearer token.

## Preparing the vector store

The voltage retrieval flow depends on an existing Qdrant collection. Review the notebooks in `notebooks/`, especially:

- `notebooks/create_collection.ipynb`
- `00.install.ipynb`

Use them to create/populate the Qdrant collection expected by the application. If the collection name or embedding model changes, update `agents/configs.py`.

## Running the application

Start the FastAPI server:

```powershell
python app.py
```

The API runs locally at:

```text
http://127.0.0.1:8000
```

You can also start it directly with Uvicorn:

```powershell
uvicorn app:fastapi_app --host 127.0.0.1 --port 8000 --reload
```

## API endpoints

All endpoints require an `Authorization` header:

```text
Authorization: Bearer <conversation-or-user-token>
```

Request body:

```json
{
  "question": "What are the hazards in Dandenong Substation?"
}
```

### `POST /run-graph`

Runs the full router-based workflow. This is the main endpoint.

### `POST /eam-run-graph`

Runs the EAM-only workflow.

### `POST /measurements-run-graph`

Runs the measurements-only workflow.

## Example requests

Full workflow:

```powershell
curl -X POST "http://127.0.0.1:8000/run-graph" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer demo-token" `
  -d "{\"question\":\"What is anodic index?\"}"
```

Measurements workflow:

```powershell
curl -X POST "http://127.0.0.1:8000/measurements-run-graph" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer demo-token" `
  -d "{\"question\":\"What is the average value of voltage in the measurements for month of October?\"}"
```

Expected response shape:

```json
{
  "result": "...",
  "datasource": "web_search"
}
```

For SQL-backed flows, `result` may also be a list of records.

## Example questions

See `docs/q.md` for sample prompts such as:

- `What are the measurements for the AssetGroup BAY_REPLACEMENT_PROGRAM?`
- `What are the hazards in Dandenong Substation?`
- `What is Rated peak withstand current?`

## How the workflow operates

1. FastAPI receives a question and bearer token.
2. LangGraph routes the question to `EAM`, `measurements`, `voltage`, or `web_search`.
3. The selected node retrieves documents, performs web search, or generates SQL and queries DuckDB.
4. Azure OpenAI produces the final answer from the retrieved context.
5. Cosmos DB stores conversation context associated with the token.

## Known setup caveats

- `.env.sample` is incomplete for the current codebase; use the expanded template above.
- The project assumes the Qdrant collection already exists and is populated.
- The response path depends on external services being reachable: Azure OpenAI, Qdrant, Tavily, and Cosmos DB.
- `requirements.txt` does not pin versions, so environment drift is possible across installs.

## Troubleshooting

- `401 Authorization header missing`: include `Authorization: Bearer <token>` in the request.
- Qdrant connection errors: verify `QDRANT_URL`, `QDRANT_KEY`, and that the expected collection exists.
- Azure OpenAI failures: verify endpoint, API key, deployment name, and API version.
- Cosmos DB failures: verify endpoint, key, database, and container names.
- Empty SQL-backed results: confirm the DuckDB files contain the expected tables and data.

## Development notes

- Main orchestration logic: `agents/maintainance.py`
- HTTP layer: `app.py`
- Router: `agents/question_router.py`
- Retrieval: `agents/retrieve.py`
- Web search fallback: `agents/web_generate.py`
- SQL generation: `agents/generate_sql.py`
