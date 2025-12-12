from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import models
from database import engine, get_db

# Создаем таблицы в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CookWizard API")


# Pydantic схемы
class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    cooking_time: int
    difficulty: str


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int

    class Config:
        orm_mode = True


# Эндпоинты
@app.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.RecipeDB(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.get("/recipes/", response_model=List[Recipe])
def get_all_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(models.RecipeDB).offset(skip).limit(limit).all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.RecipeDB).filter(models.RecipeDB.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.get("/recipes/search/", response_model=List[Recipe])
def search_recipes(
        ingredients: str,
        max_time: Optional[int] = None,
        difficulty: Optional[str] = None,
        db: Session = Depends(get_db)
):
    user_ingredients = [i.strip().lower() for i in ingredients.split(",")]

    query = db.query(models.RecipeDB)

    recipes = query.all()

    results = []
    for recipe in recipes:
        recipe_ingredients = [i.lower() for i in (recipe.ingredients or [])]
        matches = set(user_ingredients) & set(recipe_ingredients)
        if matches:
            recipe_dict = {
                "id": recipe.id,
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions,
                "cooking_time": recipe.cooking_time,
                "difficulty": recipe.difficulty,
                "match_score": len(matches)
            }
            results.append(recipe_dict)

    filtered_results = []
    for recipe in results:
        if max_time and recipe["cooking_time"] > max_time:
            continue
        if difficulty and recipe["difficulty"] != difficulty.lower():
            continue
        filtered_results.append(recipe)

    filtered_results.sort(key=lambda x: x["match_score"], reverse=True)


    for recipe in filtered_results:
        recipe.pop("match_score")

    return filtered_results


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
            "docs": "/docs",
            "health": "/health"
        }
    }
