# LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
import asyncio
import os
import random
import time
import json
import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# INITIALIZATION
load_dotenv()

app = FastAPI(
    title="Arquitectura Telemàtica de Consultes Concurrents (LLMs)",
    description="Backend asíncron amb medició de latència total (TTFT) i ample de banda",
    version="1.0.0"
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
    models: list[str]

class ModelResponse(BaseModel):
    model_name: str
    response_text: str
    latency: float       # Total time
    ttft: float          # Time To First Token
    token_count: int

# CORE FUNCTIONS (LLM HANDLERS)

async def call_ollama_model(model_id: str, display_name: str, prompt: str) -> ModelResponse:
    """
    Connexió asíncrona real per streaming a qualsevol model d'Ollama local.
    Calcula el TTFT detectant l'arribada del primer paquet TCP útil.
    """
    start_time = time.time()
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_id,
        "prompt": prompt,
        "stream": True # Streaming ENABLE
    }
    
    ttft = 0.0
    full_response = ""
    token_count = 0

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                # READ JSON that arrives
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        
                        # Capture the exact time of the first token (TTFT)
                        if ttft == 0.0:
                            ttft = time.time() - start_time
                            
                        full_response += data.get("response", "")
                        token_count += 1
                        
        total_latency = time.time() - start_time
        
        return ModelResponse(
            model_name=display_name,
            response_text=full_response,
            latency=round(total_latency, 3),
            ttft=round(ttft, 3),
            token_count=token_count
        )
    except Exception as e:
        return ModelResponse(
            model_name=display_name,
            response_text=f"Error de xarxa: Assegurat que el model '{model_id}' està descarregat a Ollama. Detall: {str(e)}",
            latency=round(time.time() - start_time, 3),
            ttft=0.0,
            token_count=0
        )

async def call_mock_api(display_name: str, prompt: str) -> ModelResponse:
    """Simula una crida a una API externa de pagament (ex: ChatGPT)."""
    start_time = time.time()
    
    # MOCK TTFT 
    ttft_delay = random.uniform(0.3, 0.9)
    await asyncio.sleep(ttft_delay)
    ttft = time.time() - start_time
    
    # MOCK time to response
    await asyncio.sleep(random.uniform(1.0, 2.5))
    total_latency = time.time() - start_time
    
    return ModelResponse(
        model_name=display_name,
        response_text=f"[{display_name} - SIMULACIÓ API] Resposta generada correctament per al prompt: '{prompt[:30]}...'",
        latency=round(total_latency, 3),
        ttft=round(ttft, 3),
        token_count=len(prompt.split()) + 30
    )

async def call_dynamic_mock(model_name: str, prompt: str) -> ModelResponse:
    """Fallback: Si s'introdueix un model desconegut, el simulem automàticament."""
    return await call_mock_api(model_name, prompt)


# DICTONARY
MODEL_ROUTERS = {
    "Llama 3 (Local - Meta)": lambda p: call_ollama_model("llama3", "Llama 3 (Local - Meta)", p),
    "DeepSeek Coder (Local)": lambda p: call_ollama_model("deepseek-coder", "DeepSeek Coder (Local)", p),
    "ChatGPT-3.5 Turbo (OpenAI)": lambda p: call_mock_api("ChatGPT-3.5 Turbo (OpenAI)", p),
    "ChatGPT-4o (OpenAI)": lambda p: call_mock_api("ChatGPT-4o (OpenAI)", p),
    "Claude 3.5 Sonnet (Anthropic)": lambda p: call_mock_api("Claude 3.5 Sonnet (Anthropic)", p),
    "Gemini 1.5 Pro (Google)": lambda p: call_mock_api("Gemini 1.5 Pro (Google)", p)
}

# ENDPOINTS

@app.get("/")
def read_root():
    return {"Status": "ONLINE", "project": "TFG Enginyeria Telecomunicacions - Arquitectura Concurrent"}

@app.post("/generate", response_model=list[ModelResponse])
async def generate_response(request: QueryRequest):
    try:
        tasks = []
        
        for model in request.models:
            handler = MODEL_ROUTERS.get(model)
            if handler:
                tasks.append(handler(request.prompt))
            else:

                tasks.append(call_dynamic_mock(model, request.prompt))

        results = await asyncio.gather(*tasks)

        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))