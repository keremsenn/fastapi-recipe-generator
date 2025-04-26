from pydantic import BaseModel

class RecipeResponse(BaseModel):
    recipe_name: str
    ingredients: list[str]
    steps: list[str]
    # Örnek: {"recipe_name": "Pankek", "ingredients": ["un", "süt"], ...}