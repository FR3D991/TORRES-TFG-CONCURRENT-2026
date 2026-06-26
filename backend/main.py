# LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
import asyncio
import os
import random
import time
import httpx # Critical for real asynchronous HTTP requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# INITIALIZATION
load_dotenv()

app = FastAPI(
    title="Creació d'una arquitectura web per fer consultes concurrents a ChatGpt, DeepSeek i LlaMa",
    description="Backend dissenyat per fer consultes a ChatGPT, DeepSeek i Llama simultàniament.",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REQUEST/RESPONSE MODELS
class QueryRequest(BaseModel):
    prompt: str
    models: list[str] = ["ChatGPT", "DeepSeek", "Llama3"]

class ModelResponse(BaseModel):
    model_name: str
    response_text: str
    latency: float
    token_count: int

# --- LLM HANDLERS ---

async def call_llama3_local(prompt: str) -> ModelResponse:
    """
    Real asynchronous call to a local Llama 3 using Ollama.
    It requires Ollama running locally with the llama3 model downloaded.
    """
    start_time = time.time()
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # We use httpx.AsyncClient() so it doesn't block the execution thread
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            latency = time.time() - start_time
            response_text = data.get("response", "Error al llegir la resposta")
            
            return ModelResponse(
                model_name="Llama3",
                response_text=response_text,
                latency=round(latency, 3),
                token_count=data.get("eval_count", len(response_text.split())) # Real tokens if Ollama provides it
            )
    except Exception as e:
        # Fallback in case Ollama is not running
        return ModelResponse(
            model_name="Llama3",
            response_text=f"Error de connexió local: Assegurat que Ollama està encès. Detall: {str(e)}",
            latency=round(time.time() - start_time, 3),
            token_count=0
        )

async def call_mock_chatgpt(prompt: str) -> ModelResponse:
    """Simulate ChatGPT call"""
    start_time = time.time()
    await asyncio.sleep(random.uniform(1.5, 2.5))
    latency = time.time() - start_time
    return ModelResponse(
        model_name="ChatGPT",
        response_text=f"[Mock ChatGPT] Resposta per a: '{prompt[:30]}...'",
        latency=round(latency, 3),
        token_count=len(prompt.split()) + 20
    )

async def call_mock_deepseek(prompt: str) -> ModelResponse:
    """Simulate DeepSeek call"""
    start_time = time.time()
    await asyncio.sleep(random.uniform(0.8, 1.5))
    latency = time.time() - start_time
    return ModelResponse(
        model_name="DeepSeek",
        response_text=f"[Mock DeepSeek] Resposta per a: '{prompt[:30]}...'",
        latency=round(latency, 3),
        token_count=len(prompt.split()) + 15
    )

async def call_dynamic_mock(model_name: str, prompt: str) -> ModelResponse:
    """Fallback dinàmic: si el frontend demana un model que no existeix, es auto-simula."""
    start_time = time.time()
    await asyncio.sleep(random.uniform(1.0, 2.0)) # Simulamos latencia
    latency = time.time() - start_time
    return ModelResponse(
        model_name=model_name,
        response_text=f"[{model_name} - MOCK DINÀMIC] Resposta generada automàticament per al prompt: '{prompt[:20]}...'",
        latency=round(latency, 3),
        token_count=len(prompt.split()) + 10
    )

#MODEL ROUTER DICTIONARY
MODEL_ROUTERS = {
    "Llama3": call_llama3_local,
    "ChatGPT": call_mock_chatgpt,   # Change to real function when you have API Key
    "DeepSeek": call_mock_deepseek  # Change to real function when you have API Key
}

# ENDPOINTS

@app.get("/")
def read_root():
    return {"Status": "ONLINE", "project": "TFG Enginyeria Telecomunicacions"}

@app.post("/generate", response_model=list[ModelResponse])
async def generate_response(request: QueryRequest):
    try:
        tasks = []
        
        for model in request.models:
            handler = MODEL_ROUTERS.get(model)
            if handler:
                tasks.append(handler(request.prompt))
            else:
                # ¡LA MAGIA! Si el modelo no existe, usamos el mock dinámico auto-generado
                tasks.append(call_dynamic_mock(model, request.prompt))

        # Execute all LLM calls concurrently
        results = await asyncio.gather(*tasks)

        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))