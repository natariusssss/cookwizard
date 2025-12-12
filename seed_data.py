import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

# Тестовые рецепты
test_recipes = [
    {
        "title": "Курица с картошкой",
        "ingredients": ["курица", "картошка", "лук", "морковь", "соль", "перец"],
        "instructions": "1. Нарезать курицу и овощи\n2. Обжарить курицу\n3. Добавить овощи\n4. Тушить 30 минут",
        "cooking_time": 40,
        "difficulty": "easy"
    },
    {
        "title": "Яичница с помидорами",
        "ingredients": ["яйца", "помидоры", "соль", "перец", "масло"],
        "instructions": "1. Нарезать помидоры\n2. Разбить яйца\n3. Жарить 5-7 минут",
        "cooking_time": 10,
        "difficulty": "easy"
    },
    {
        "title": "Суп куриный",
        "ingredients": ["курица", "картошка", "лук", "морковь", "вермишель", "соль"],
        "instructions": "1. Сварить бульон из курицы\n2. Добавить овощи\n3. Добавить вермишель\n4. Варить 20 минут",
        "cooking_time": 60,
        "difficulty": "medium"
    },
    {
        "title": "Салат овощной",
        "ingredients": ["помидоры", "огурцы", "лук", "масло", "соль", "перец"],
        "instructions": "1. Нарезать овощи\n2. Посолить, поперчить\n3. Заправить маслом",
        "cooking_time": 15,
        "difficulty": "easy"
    },
    {
        "title": "Плов",
        "ingredients": ["рис", "курица", "лук", "морковь", "чеснок", "специи"],
        "instructions": "1. Обжарить курицу с овощами\n2. Добавить рис и воду\n3. Тушить 40 минут",
        "cooking_time": 60,
        "difficulty": "medium"
    }
]


def seed_database():
    db = SessionLocal()

    existing = db.query(models.RecipeDB).count()
    if existing > 0:
        print(f"В базе уже есть {existing} рецептов. Пропускаем заполнение.")
        db.close()
        return

    for recipe_data in test_recipes:
        recipe = models.RecipeDB(**recipe_data)
        db.add(recipe)

    db.commit()
    print(f"Добавлено {len(test_recipes)} тестовых рецептов.")
    db.close()


if __name__ == "__main__":
    seed_database()