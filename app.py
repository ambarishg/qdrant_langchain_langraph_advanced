from fastapi import FastAPI, HTTPException, Request,Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents.maintainance import run_app, run_eam_app,run_measurements_app
from pydantic import BaseModel

async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = token.replace("Bearer ", "")
    return token

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
async def run_graph(input_data: InputData,token=Depends(get_current_user)):
    
    try:
        result , datasource = run_app(input_data.question,token)
        return {"result": result , "datasource": datasource}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fastapi_app.post("/eam-run-graph")
async def eam_run_graph(input_data: InputData,token=Depends(get_current_user)):
    
    try:
        result , datasource = run_eam_app(input_data.question,token)
        return {"result": result , "datasource": datasource}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@fastapi_app.post("/measurements-run-graph")
async def measurements_run_graph(input_data: InputData,
                        token=Depends(get_current_user)):
    
    try:
        result , datasource = run_measurements_app(input_data.question,token)
        return {"result": result , "datasource": datasource}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("app:fastapi_app", host="127.0.0.1", port=8000, reload=True)

