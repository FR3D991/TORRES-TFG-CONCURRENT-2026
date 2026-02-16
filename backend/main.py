
#LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
import asyncio
import os
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

#INITIALIZATION
load_dotenv() #Load .env variables (API Keys)

app = FastAPI(
    title="Creació d'una arquitectura web per fer consultes concurrents a ChatGpt, DeepSeek i LlaMa"
    description="Backend dissenyat per fer consultes a ChatGPT, DeepSeek i Llama simultàniament, tot plegat per veure respostes i comparar"
    version="0.1.0"
)

app.add_middleware( #Allows the communication
    CORSMiddleware,
    allow_origins=["*"], #This project (TFG) we allow all (*) origin web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#REQUEST/RESPONSE
class QueryRequest(BaseModel):
    prompt: str
    models: list[str] = ["ChatGPT", "DeepSeek", "Llama3"] #Default Models

class ModelResponse(BaseModel):
    model_name: str
    response_text: str
    latency: float
    token_count: int #Sustainability


#MOCKING
async def call_llm_service(model_name: str, prompt: str) -> ModelResponse:
    """
    Simulate asynchronous call to a LLM
    Args:
        model_name: Model Name
        prompt: User question
    """
    #Time response simulation (seconds) 
    latencies = {
        "ChatGPT": random.uniform(1.5, 2.5),
        "DeepSeek": random.uniform(0.8, 1.5),
        "Llama3": random.uniform(2.5, 4.0)
    }

    delay = latencies.get(model_name, 2.0) #Save the time that it needs to respond depending on the model, if it doesn't exist use 2 sec

    await asyncio.sleep(delay) #Free the processor to do other things while it waits (simulate real time that needs the API to response)

    return ModelResponse(
        model_name=model_name,
        response_text=f"[{model_name}] Resposta simulada a: '{prompt[:30]}...'. Això es una proba del BACKEND"
        latency=round(delay,3),
        token_count=len(prompt.split())+20 #IA coin. Simple estimation, tokens = words or fragments words
    )


#ENDPOINT
@app.get("/")
def read_root():
    return{"status": "onLine", "project": "TFG Enginyeria Telecomunicacions", "env": os.getenv("ENV")} #Health endpoint to verify that the server works correctly

@app.post("/generate", response_model=list[ModelResponse])
async def generate_response(request: QueryRequest):
    try:
        tasks = []
        for model in request