from config import Config
from fastapi import FastAPI
from app.api.recipe_api import router as recipe_router


app = FastAPI()
app.state.config = Config
app.include_router(recipe_router)
