from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
        ingredients: Optional[str] = Query(None, description="Ингредиенты через запятую"),
        title: Optional[str] = Query(None, description="Название рецепта (поиск по части названия)"),
        max_time: Optional[int] = None,
        difficulty: Optional[str] = None,
        db: Session = Depends(get_db)
):

    print(f"🔍 ПОИСК ВЫЗВАН: ingredients={ingredients}, title={title}")
    query = db.query(models.RecipeDB)

    if ingredients:
        user_ingredients = [i.strip().lower() for i in ingredients.split(",")]
        conditions = []
        for ingredient in user_ingredients:
            conditions.append(models.RecipeDB.ingredients.any(ingredient))

        if conditions:
            query = query.filter(or_(*conditions))

    if title:
        title_lower = title.lower()
        query = query.filter(models.RecipeDB.title.ilike(f"%{title_lower}%"))
    if max_time:
        query = query.filter(models.RecipeDB.cooking_time <= max_time)
    if difficulty:
        query = query.filter(models.RecipeDB.difficulty == difficulty.lower())
    recipes = query.all()
    results = []
    for recipe in recipes:
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


@app.get("/api/search/title/{title_part}")
def search_by_title(
        title_part: str,
        db: Session = Depends(get_db)
):

    recipes = db.query(models.RecipeDB) \
        .filter(models.RecipeDB.title.ilike(f"%{title_part}%")) \
        .all()

    results = []
    for recipe in recipes:
        results.append({
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "cooking_time": recipe.cooking_time,
            "difficulty": recipe.difficulty,
        })

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
        "message": "CookWizard API v3",
        "endpoints": {
            "search": "/api/search?ingredients=chicken,potato&title=курица",
            "search_by_title": "/api/search/title/{title_part}",
            "all_recipes": "/api/recipes",
            "get_recipe": "/api/recipes/{id}",
            "docs": "/docs"
        }
    }
