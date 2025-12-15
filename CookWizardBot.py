from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import asyncio
import os;
dp = Dispatcher()
token=os.getenv("BOT_TOKEN")
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
    await message.answer(f"Найдём: {full_query}")
@dp.message(Command("product")) 
async def  search(message: Message):
    name = message.text.split()[1:]
    if not name:
        await message.answer("Использование: /product <название ингредиента>, <название ингредиента>, ...")
        return
    full = "".join(name)
    ingredients = full.split(",")
    await message.answer(ingredients[1])
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
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

