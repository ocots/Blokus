from fastapi import APIRouter
from typing import List
from api.models import AIModelInfo
from blokus.rl.registry import get_registry

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/models", response_model=List[AIModelInfo])
def list_ai_models():
    """List all available AI models/personas."""
    registry = get_registry()
    # Force reload to get latest updates (e.g. newly trained models)
    registry.reload()
    return registry.list_for_api(only_enabled=True)
