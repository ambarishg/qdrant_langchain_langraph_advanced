from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents.maintainance import run_app
from pydantic import BaseModel

# Define input schema using Pydantic
class InputData(BaseModel):
    question: str  # adjust fields based on your input structure

fastapi_app = FastAPI()

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.post("/run-graph")
async def run_graph(input_data: InputData):
    
    try:
        result = run_app(input_data.question)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:fastapi_app", host="127.0.0.1", port=8000, reload=True)

