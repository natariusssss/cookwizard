from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import requests
import asyncio
import os;
dp = Dispatcher()
token=os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")
class Api:
    def __init__(self, base_url: str):
        self.base_url = base_url
    async def search_recipe_by_ingredients(self, ingredients : str):
        param = {
            "ingredients" : ingredients
        }
        responce = requests.get(f"{self.base_url}/api/search", timeout=5, params=param)
        return responce.json()
    async def Search_recipe_by_name(self,  name: str):
        try:
            param = {
                "title" : name
            }
            responce = requests.get(f"{self.base_url}/api/search", params=param)
            return responce.json()
        except requests.exceptions.RequestException as e:
            return None
        
api = Api(API_URL)       
bot = Bot(token)
@dp.message(Command("start"))
async def start(message:types.Message):
    await message.answer("Привет! Я CookWizard бот")
@dp.message(Command("name"))
async def search_name(message: Message):
    name = message.text.split()[1:] 
    if not name:
        await message.answer("Использование: /name <название блюда>")
        return
    full_query = "".join(name)
    recipe = await api.Search_recipe_by_name(full_query)
    dp.current_user_data = recipe
    if recipe:
        answer = "🍳 Найденные рецепты:\n\n"
        for i, rec in enumerate(recipe, 1):
            answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
        answer += "\n📝 Для просмотра рецепта введите его номер:"
        await message.answer(answer)
        dp.current_user_data = recipe
@dp.message(Command("product")) 
async def  search(message: Message):
    name = message.text.split()[1:]
    if not name:
        await message.answer("Использование: /product <название ингредиента>, <название ингредиента>, ...")
        return
    full = "".join(name)
    recipe = await api.search_recipe_by_ingredients(full)
    dp.current_user_data = recipe
    if recipe:
        answer = "🍳 Найденные рецепты:\n\n"
        for i, rec in enumerate(recipe, 1):
            answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
        answer += "\n📝 Для просмотра рецепта введите его номер:"
        await message.answer(answer)
        dp.current_user_data = recipe
@dp.message(lambda message: message.text.isdigit())
async def select_recipe(message: Message):
    if hasattr(dp, 'current_user_data'):
        recipes = dp.current_user_data
        number = int(message.text)
        if 1 <= number <= len(recipes):
            recipe = recipes[number - 1]
            text = f"""
<b>{recipe['title']}</b>

🎯Сложность: {recipe['difficulty']}
⏱️Время приготовления: {recipe['cooking_time']} мин
📋Инструкция: 
{recipe['instructions']}
            """
            await message.answer(text, parse_mode=ParseMode.HTML)
        else:
            await message.answer("❌ Неверный номер рецепта")
    
@dp.message(Command("help"))
async def help(message: Message):
    text = """
<b>Список команд бота:</b>

👋 <b>Базовые команды:</b>
/start - Приветствие бота
/help - список команд

🔍 <b>Поиск рецептов:</b>
/name &ltназвание блюда&gt - поиск рецепта по имени
/product &ltингредиент1&gt, &ltингредиент2&gt, ... - поиск рецептов по ингредиентам
    """
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message()
async def handle_any_message(message: Message):
    await message.answer("Неизвестная команда. Введите /help для вывода списка всех доступных команд")
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

