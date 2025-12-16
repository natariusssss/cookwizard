from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CookWizard API")

app.router.redirect_slashes = False


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


@app.get("/api/search")
def search_recipes(
        ingredients: str = Query(..., description="Ингредиенты через запятую"),
        max_time: Optional[int] = None,
        difficulty: Optional[str] = None,
        db: Session = Depends(get_db)
):

    print(f"🔍 ПОИСК ВЫЗВАН: {ingredients}")

    user_ingredients = [i.strip().lower() for i in ingredients.split(",")]

    recipes = db.query(models.RecipeDB).all()

    results = []
    for recipe in recipes:
        if not recipe.ingredients:
            continue

        recipe_ingredients = [i.lower() for i in recipe.ingredients]
        matches = set(user_ingredients) & set(recipe_ingredients)

        if matches:
            if max_time and recipe.cooking_time > max_time:
                continue
            if difficulty and recipe.difficulty != difficulty.lower():
                continue

            results.append({
                "id": recipe.id,
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions,
                "cooking_time": recipe.cooking_time,
                "difficulty": recipe.difficulty,
            })

    print(f"✅ Найдено {len(results)} рецептов")
    return results


@app.get("/api/recipes")
def get_all_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(models.RecipeDB).offset(skip).limit(limit).all()
    return recipes


@app.get("/api/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.RecipeDB).filter(models.RecipeDB.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.post("/api/recipes")
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.RecipeDB(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {
        "message": "CookWizard API v2",
        "endpoints": {
            "search": "/api/search?ingredients=chicken,potato",
            "all_recipes": "/api/recipes",
            "get_recipe": "/api/recipes/{id}",
            "docs": "/docs"
        }
    }
