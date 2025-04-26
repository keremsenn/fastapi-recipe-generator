from app.service.recipe_service import generate_recipe
from app.model.recipe_model import RecipeResponse
from fastapi import APIRouter

router = APIRouter()
@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/generate-recipe/", response_model=RecipeResponse)
async def get_recipe(ingredients: list[str]):
    return generate_recipe(ingredients)
