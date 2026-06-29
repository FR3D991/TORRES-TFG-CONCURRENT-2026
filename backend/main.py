# -LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
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

# -INITIALIZATION
load_dotenv()

app = FastAPI(
    title="Creació d'una arquitectura web per fer consultes concurrents a ChatGpt, DeepSeek i LlaMa",
    description="Backend asíncron per medició mètriques a diferents LLMs",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -REQUEST/RESPONSE MODELS
class QueryRequest(BaseModel):
    prompt: str
    models: list[str]

class ModelResponse(BaseModel):
    model_name: str
    response_text: str
    latency: float       # Total time
    ttft: float          # Time To First Token
    token_count: int

# -CORE FUNCTIONS (LLM HANDLERS)
async def call_mock_api(display_name: str, prompt: str, is_fallback: bool = False) -> ModelResponse:
    """Simula una crida a una API. Si actua com a Fallback (ERROR de clau), avisa l'usuari sobre el .env.example"""
    start_time = time.time()
    
    # Time delay mock
    ttft_delay = random.uniform(0.3, 0.9)
    await asyncio.sleep(ttft_delay)
    ttft = time.time() - start_time
    await asyncio.sleep(random.uniform(1.0, 2.5))
    total_latency = time.time() - start_time
    
    # If there's no API KEYS
    if is_fallback:
        resposta = (f"[{display_name}] Això és una simulació, ja que no s'han detectat "
                    f"les 'API Keys' PERSONALS corresponents. Si vols respostes reals, recorda crear un arxiu "
                    f"'.env' posant les teves claus, utilitzant el '.env.example' com a plantilla.")
    else:
        resposta = f"[{display_name} - SIMULACIÓ API] Resposta generada automàticament per al prompt: '{prompt[:30]}...'"
    
    return ModelResponse(
        model_name=display_name,
        response_text=resposta,
        latency=round(total_latency, 3),
        ttft=round(ttft, 3),
        token_count=len(prompt.split()) + 30
    )

async def call_ollama_model(model_id: str, display_name: str, prompt: str) -> ModelResponse:
    """Connexió asíncrona real per streaming a qualsevol model d'Ollama local."""
    start_time = time.time()
    url = "http://localhost:11434/api/generate"
    payload = {"model": model_id, "prompt": prompt, "stream": True}
    
    ttft, token_count = 0.0, 0
    full_response = ""

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if ttft == 0.0:
                            ttft = time.time() - start_time
                        full_response += data.get("response", "")
                        token_count += 1
                        
        total_latency = time.time() - start_time
        return ModelResponse(
            model_name=display_name, response_text=full_response,
            latency=round(total_latency, 3), ttft=round(ttft, 3), token_count=token_count
        )
    except Exception as e:
        return ModelResponse(
            model_name=display_name,
            response_text=f"Error de xarxa: Assegurat que el model '{model_id}' està descarregat a Ollama. Detall: {str(e)}",
            latency=round(time.time() - start_time, 3), ttft=0.0, token_count=0
        )

async def call_generic_cloud_api(model_id: str, display_name: str, prompt: str, env_key_name: str, base_url: str) -> ModelResponse:
    """
    CLASSE/FUNCIÓ GENÈRICA: Permet integrar qualsevol proveïdor Cloud que utilitzi 
    l'estàndard d'OpenAI (OpenAI, DeepSeek Cloud...).
    Inclou Graceful Degradation (Tolerància a fallades si no hi ha clau).
    """
    api_key = os.getenv(env_key_name)
    if not api_key or api_key.startswith("API_KEY_") or api_key == "":
        return await call_mock_api(display_name, prompt, is_fallback=True)

    start_time = time.time()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "stream": True}
    
    ttft, token_count = 0.0, 0
    full_response = ""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", base_url, headers=headers, json=payload) as response:
                # API KEY error 401
                if response.status_code == 401:
                    return await call_mock_api(display_name, prompt, is_fallback=True)
                
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = json.loads(line[6:])
                        if ttft == 0.0:
                            ttft = time.time() - start_time
                        delta = data["choices"][0].get("delta", {}).get("content", "")
                        if delta:
                            full_response += delta
                            token_count += 1
                            
        total_latency = time.time() - start_time
        return ModelResponse(
            model_name=display_name, response_text=full_response,
            latency=round(total_latency, 3), ttft=round(ttft, 3), token_count=token_count
        )
    except Exception as e:
        return ModelResponse(
            model_name=display_name, response_text=f"Error d'API ({env_key_name}): {str(e)}",
            latency=round(time.time() - start_time, 3), ttft=0.0, token_count=0
        )

# -DICTIONARY
MODEL_ROUTERS = {
    # Local
    "Llama 3 (Local - Meta)": lambda p: call_ollama_model("llama3", "Llama 3 (Local - Meta)", p),
    "DeepSeek Coder (Local)": lambda p: call_ollama_model("deepseek-coder", "DeepSeek Coder (Local)", p),
    "DeepSeek LLM (Local - General)": lambda p: call_ollama_model("deepseek-llm", "DeepSeek LLM (Local - General)", p),
    
    # Cloud (OpenAI Standard)
    "ChatGPT-3.5 Turbo (OpenAI)": lambda p: call_generic_cloud_api(
        "gpt-3.5-turbo", "ChatGPT-3.5 Turbo (OpenAI)", p, "OPENAI_API_KEY", "https://api.openai.com/v1/chat/completions"
    ),
    "ChatGPT-4o (OpenAI)": lambda p: call_generic_cloud_api(
        "gpt-4o", "ChatGPT-4o (OpenAI)", p, "OPENAI_API_KEY", "https://api.openai.com/v1/chat/completions"
    ),
    "DeepSeek Cloud (API Oficial)": lambda p: call_generic_cloud_api(
        "deepseek-chat", "DeepSeek Cloud (API Oficial)", p, "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1/chat/completions"
    ),
    
    # Mock external models
    "Claude 3.5 Sonnet (Anthropic)": lambda p: call_mock_api("Claude 3.5 Sonnet (Anthropic)", p),
    "Gemini 1.5 Pro (Google)": lambda p: call_mock_api("Gemini 1.5 Pro (Google)", p)
}

# -ENDPOINTS
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
                tasks.append(call_mock_api(model, request.prompt))

        results = await asyncio.gather(*tasks)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))