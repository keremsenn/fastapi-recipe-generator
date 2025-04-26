import requests
from config import Config
from ..model.recipe_model import RecipeResponse
from typing import List
import re


def generate_recipe(ingredients: List[str]) -> RecipeResponse:
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "HTTP-Referer": Config.OPENROUTER_APP_NAME,
        "Content-Type": "application/json"
    }
    prompt = (
        "USE ONLY ENGLISH. Create a REALISTIC recipe using the following EDIBLE ingredients:\n"
        f"Ingredients: {', '.join(ingredients)}\n\n"
        "RULES:\n"
        "1. All ingredients must be EDIBLE (do NOT use stones, sand, plastic etc.)\n"
        "2. The recipe must be PRACTICALLY EXECUTABLE in a kitchen\n"
        "3. Never go beyond the given ingredients\n"
        "4. Measurements must be clearly given in grams/ml/degrees\n"
        "5. Steps should sound like they were written by a professional chef\n\n"
        "IF INGREDIENTS ARE INEDIBLE, RETURN THIS MESSAGE:\n"
        "**Warning**: The ingredients contain non-edible items (stones, sand etc.). Please only enter edible food items.\n\n"
        "FORMAT:\n"
        "**Recipe Name**: [Name]\n"
        "**Ingredients**:\n- [Item 1]\n- [Item 2]\n"
        "**Instructions**:\n1. [Step 1]\n2. [Step 2]"
    )
    payload = {
        "model": Config.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": Config.MAX_TOKENS,
        "temperature": Config.TEMPERATURE
    }
    try:
        response = requests.post(
            Config.OPENROUTER_API_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        # OpenRouter'dan gelen yanıt formatı
        raw_text = response.json()['choices'][0]['message']['content']
        # Debug için yanıtı kontrol edelim
        print("API yanıtı:", raw_text)

        # Tarif adını bulma - İNGİLİZCE
        name_match = re.search(r"\*\*Recipe Name\*\*:?\s*(.+?)(?:\n|$)", raw_text)
        recipe_name = name_match.group(1).strip() if name_match else "Unnamed Recipe"

        # Malzemeleri bulma - İNGİLİZCE
        ingredients_section = re.search(
            r"\*\*Ingredients\*\*:?\s*([\s\S]+?)(?:\*\*(?:Instructions|Steps|Method|Preparation)\*\*|$)", raw_text)
        ingredients_list = []
        if ingredients_section:
            ingredients_text = ingredients_section.group(1)
            ingredients_list = [item.strip() for item in re.findall(r"[-•*]\s*(.+?)(?:\n|$)", ingredients_text)]

        # Hazırlanış adımlarını bulma - İNGİLİZCE
        steps_section = re.search(r"\*\*(?:Instructions|Steps|Method|Preparation)\*\*:?\s*([\s\S]+)$", raw_text)
        steps_list = []
        if steps_section:
            steps_text = steps_section.group(1)
            steps_list = [step.strip() for step in re.findall(r"\d+\.?\s*(.+?)(?:\n|$)", steps_text)]

        # Uyarı mesajı kontrolü
        warning_match = re.search(r"\*\*Warning\*\*:.*?non-edible", raw_text, re.IGNORECASE)
        if warning_match:
            return RecipeResponse(
                recipe_name="Warning: Inedible Ingredients",
                ingredients=[],
                steps=["The ingredients contain non-edible items. Please only enter edible food items."]
            )

        return RecipeResponse(
            recipe_name=recipe_name,
            ingredients=ingredients_list if ingredients_list else [ing.strip() for ing in ingredients],
            steps=steps_list if steps_list else ["No steps information available."]
        )
    except Exception as e:
        print(f"Error details: {str(e)}")
        return RecipeResponse(
            recipe_name="Error Occurred",
            ingredients=[],
            steps=[f"API error: {str(e)}"]
        )