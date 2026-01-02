from fastapi import APIRouter, Request

from ..registry import ModelRegistry
from ..schemas import ModelList, ModelObject

router = APIRouter(tags=["models"])


@router.get("/v1/models", response_model=ModelList)
async def list_models(request: Request) -> ModelList:
    registry: ModelRegistry = request.app.state.registry
    return ModelList(
        data=[
            ModelObject(id=spec.name, loaded=registry.is_loaded(spec.name))
            for spec in registry.list_specs()
        ]
    )
