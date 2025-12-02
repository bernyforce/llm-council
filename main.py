from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import json
import os
import asyncio
from datetime import datetime
import uuid

app = FastAPI(title="LLM Council API")

# CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
COUNCIL_MODELS = json.loads(os.getenv("COUNCIL_MODELS", '["openai/gpt-4-turbo","anthropic/claude-3-opus-20240229","google/gemini-pro"]'))
CHAIRMAN_MODEL = os.getenv("CHAIRMAN_MODEL", "google/gemini-pro")

# Modèles Pydantic
class QueryRequest(BaseModel):
    query: str
    
class CouncilResponse(BaseModel):
    id: str
    query: str
    first_opinions: Dict[str, str]
    reviews: Dict[str, Dict[str, Any]]
    final_response: str
    timestamp: str

# Fonction pour appeler OpenRouter
async def call_openrouter(model: str, messages: List[Dict[str, str]]) -> str:
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"OpenRouter API error: {str(e)}")

# Étape 1 : Obtenir les premières opinions
async def get_first_opinions(query: str) -> Dict[str, str]:
    tasks = []
    for model in COUNCIL_MODELS:
        messages = [{"role": "user", "content": query}]
        tasks.append(call_openrouter(model, messages))
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    opinions = {}
    for model, response in zip(COUNCIL_MODELS, responses):
        if isinstance(response, Exception):
            opinions[model] = f"Error: {str(response)}"
        else:
            opinions[model] = response
    
    return opinions

# Étape 2 : Faire les reviews croisées
async def get_reviews(query: str, opinions: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    reviews = {}
    
    for reviewer_model in COUNCIL_MODELS:
        # Anonymiser les réponses
        anonymized_responses = []
        model_mapping = {}
        for i, (model, response) in enumerate(opinions.items()):
            if model != reviewer_model:
                anonymized_responses.append(f"Response {i+1}: {response}")
                model_mapping[f"Response {i+1}"] = model
        
        review_prompt = f"""Original query: {query}

Here are the responses from other models (anonymized):

{chr(10).join(anonymized_responses)}

Please rank these responses from best to worst based on accuracy, completeness, and insight. 
Provide a brief justification for your ranking.

Format your response as:
RANKING: [Response X, Response Y, ...]
JUSTIFICATION: Your explanation here"""

        messages = [{"role": "user", "content": review_prompt}]
        
        try:
            review = await call_openrouter(reviewer_model, messages)
            reviews[reviewer_model] = {
                "review": review,
                "model_mapping": model_mapping
            }
        except Exception as e:
            reviews[reviewer_model] = {
                "review": f"Error: {str(e)}",
                "model_mapping": model_mapping
            }
    
    return reviews

# Étape 3 : Réponse finale du Chairman
async def get_final_response(query: str, opinions: Dict[str, str], reviews: Dict[str, Dict[str, Any]]) -> str:
    chairman_prompt = f"""You are the Chairman of the LLM Council. 

Original query: {query}

Council member responses:
{json.dumps(opinions, indent=2)}

Peer reviews:
{json.dumps({k: v['review'] for k, v in reviews.items()}, indent=2)}

Based on all the responses and peer reviews, provide a comprehensive, accurate, and well-structured final answer to the original query.
Synthesize the best insights from all responses while correcting any errors or misconceptions."""

    messages = [{"role": "user", "content": chairman_prompt}]
    
    try:
        return await call_openrouter(CHAIRMAN_MODEL, messages)
    except Exception as e:
        return f"Chairman error: {str(e)}"

# Endpoint principal
@app.post("/api/council", response_model=CouncilResponse)
async def council_query(request: QueryRequest):
    session_id = str(uuid.uuid4())
    
    # Étape 1 : Premières opinions
    first_opinions = await get_first_opinions(request.query)
    
    # Étape 2 : Reviews
    reviews = await get_reviews(request.query, first_opinions)
    
    # Étape 3 : Réponse finale
    final_response = await get_final_response(request.query, first_opinions, reviews)
    
    response = CouncilResponse(
        id=session_id,
        query=request.query,
        first_opinions=first_opinions,
        reviews=reviews,
        final_response=final_response,
        timestamp=datetime.now().isoformat()
    )
    
    # Sauvegarder la conversation
    os.makedirs("data/conversations", exist_ok=True)
    with open(f"data/conversations/{session_id}.json", "w") as f:
        json.dump(response.dict(), f, indent=2)
    
    return response

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "LLM Council API"}

# Servir le frontend si buildé
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="static")
    
    @app.get("/")
    async def read_index():
        return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
