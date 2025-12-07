
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="CookWizard API")


# Модель для рецепта
class Recipe(BaseModel):
    id: int
    title: str
    ingredients: List[str]
    instructions: str
    cooking_time: int
    difficulty: str = "easy"


# ТЕСТОВЫЕ ДАННЫЕ (пока без БД)
fake_recipes_db = [
    {
        "id": 1,
        "title": "Курица с картошкой",
        "ingredients": ["курица", "картошка", "лук", "морковь"],
        "instructions": "1. Обжарить курицу\n2. Добавить овощи\n3. Тушить 30 мин",
        "cooking_time": 40,
        "difficulty": "easy"
    },
    {
        "id": 2,
        "title": "Яичница",
        "ingredients": ["яйца", "соль", "перец"],
        "instructions": "1. Разбить яйца\n2. Посолить\n3. Жарить 5 мин",
        "cooking_time": 10,
        "difficulty": "easy"
    }
]


# Поиск рецептов по ингредиентам
@app.get("/recipes/search", response_model=List[Recipe])
def search_recipes(ingredients: str):

    user_ingredients = [i.strip().lower() for i in ingredients.split(",")]

    results = []

    for recipe in fake_recipes_db:
        recipe_ingredients = [i.lower() for i in recipe["ingredients"]]
        matches = set(user_ingredients) & set(recipe_ingredients)
        if matches:
            recipe_with_score = recipe.copy()
            recipe_with_score["match_score"] = len(matches)
            results.append(recipe_with_score)


    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results



@app.get("/recipes", response_model=List[Recipe])
def get_all_recipes():
    return fake_recipes_db



@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    for recipe in fake_recipes_db:
        if recipe["id"] == recipe_id:
            return recipe
    return {"error": "Recipe not found"}



@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}


@app.get("/")
def root():
    return {
        "message": "CookWizard API is running!",
        "endpoints": {
            "search": "/recipes/search?ingredients=курица,картошка",
            "all_recipes": "/recipes",
            "docs": "/docs"
        }
    }
