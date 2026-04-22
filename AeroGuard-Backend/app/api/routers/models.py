from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/models", tags=["Model Management"])

class TrainRequest(BaseModel):
    model_type: str

class CompareRequest(BaseModel):
    models: List[str]

@router.post("/train")
async def train_model(request: TrainRequest):
    return {"status": "success", "message": f"Training started for {request.model_type}"}

@router.post("/save")
async def save_model():
    return {"status": "success", "message": "Models saved successfully"}

@router.post("/load")
async def load_model():
    return {"status": "success", "message": "Models loaded successfully"}

@router.post("/compare")
async def compare_models(request: CompareRequest):
    return {"best_model": "LSTM", "metrics": {}}

@router.get("/quick-compare")
async def quick_compare():
    return {"status": "success", "comparison": {}}

@router.get("/available-models")
async def get_available_models():
    return {"available_models": [{"name": "LSTM"}, {"name": "SARIMA"}, {"name": "XGBoost"}]}

@router.get("/trained-metrics")
async def get_trained_metrics():
    return {"status": "success", "metrics": {}}
