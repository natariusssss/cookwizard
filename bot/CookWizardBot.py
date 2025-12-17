from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, BotCommand, BotCommandScopeDefault
from aiogram.enums import ParseMode
import requests
import asyncio
import os
import io
import json
import torch
from torchvision import models, transforms
from PIL import Image
INGREDIENT_TRANSLATION = {
    "banana": "банан",
    "broccoli": "брокколи",
    "strawberry": "клубника",
    "lemon": "лимон",
    "pineapple": "ананас",
    "pomegranate": "гранат",
}
dp = Dispatcher()
token = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")
def load_ml_model():
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.eval()
    with open('imagenet_classes.json') as f:
        idx_to_class = json.load(f)
    return model, idx_to_class
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
def classify_image(image: Image.Image, model, idx_to_class):
    img_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        output = model(img_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top_prob, top_catid = torch.topk(probabilities, 1)
    class_id = top_catid[0].item()
    class_info = idx_to_class[str(class_id)]
    return class_info[1].strip()
model, idx_to_class = load_ml_model()
class Api:
    def __init__(self, base_url: str):
        self.base_url = base_url
    async def search_recipe_by_ingredients(self, ingredients: str):
        param = {"ingredients": ingredients}
        responce = requests.get(f"{self.base_url}/api/search", timeout=5, params=param)
        return responce.json()
    async def Search_recipe_by_name(self, name: str):
        try:
            param = {"title": name}
            responce = requests.get(f"{self.base_url}/api/search", params=param)
            return responce.json()
        except requests.exceptions.RequestException:
            return None
    async def Search_recipe_by_time(self, time: int):
        try:
            param = {"max_time": time}
            responce = requests.get(f"{self.base_url}/api/search", params=param)
            return responce.json()
        except requests.exceptions.RequestException:
            return None
    async def Search_recipe_by_difficulty(self, diff: str):
        try:
            param = {"difficulty": diff}
            responce = requests.get(f"{self.base_url}/api/search", params=param)
            return responce.json()
        except requests.exceptions.RequestException:
            return None
api = Api(API_URL)
bot = Bot(token)
@dp.message(F.photo)
async def handle_photo_search(message: Message):
    print("Лог: Получено фото для анализа")
    photo_file = await message.bot.get_file(message.photo[-1].file_id)
    photo_bytes = await message.bot.download_file(photo_file.file_path)
    image = Image.open(io.BytesIO(photo_bytes.read()))
    product_name = classify_image(image, model, idx_to_class)
    product_name_ru = INGREDIENT_TRANSLATION.get(
        product_name.lower(),
        product_name
    )
    await message.answer(f"Я вижу на фото: <b>{product_name_ru}</b>\nИщу рецепты...", parse_mode=ParseMode.HTML)
    recipe = await api.search_recipe_by_ingredients(product_name_ru)
    if recipe:
        answer = "🍳 Найденные рецепты:\n\n"
        for i, rec in enumerate(recipe, 1):
            answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
        answer += "\n📝 Для просмотра рецепта введите его номер:"
        await message.answer(answer)
        dp.current_user_data = recipe
    else:
        await message.answer("Ничего не найдено по этому продукту.")
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я CookWizard бот\nВведите /help для отображения всех возможных команд")
@dp.message(Command("help"))
async def help_cmd(message: Message):
    text = "<b>Список команд бота:</b>\n/start, /help, /name, /product, /time, /diff\nИли просто пришли мне ФОТО ингредиента (проверка на апдейт)!"
    await message.answer(text, parse_mode=ParseMode.HTML)
@dp.message(Command("name"))
async def search_name(message: Message):
    name = message.text.split()[1:]
    if not name:
        await message.answer("Использование: /name <название блюда>")
        return
    full_query = " ".join(name)
    recipe = await api.Search_recipe_by_name(full_query)
    if recipe:
        answer = "🍳 Найденные рецепты:\n\n"
        for i, rec in enumerate(recipe, 1):
            answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
        answer += "\n📝 Для просмотра рецепта введите его номер:"
        await message.answer(answer)
        dp.current_user_data = recipe
    else:
        await message.answer("🔍❌По вашему запросу ничего не найдено")


@dp.message(Command("product"))
async def search_prod(message: Message):
    name = message.text.split()[1:]
    if not name:
        await message.answer("Использование: /product <ингредиент1>, <ингредиент2>...")
        return
    full = "".join(name)
    recipe = await api.search_recipe_by_ingredients(full)
    if recipe:
        answer = "🍳 Найденные рецепты:\n\n"
        for i, rec in enumerate(recipe, 1):
            answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
        answer += "\n📝 Для просмотра рецепта введите его номер:"
        await message.answer(answer)
        dp.current_user_data = recipe
    else:
        await message.answer("🔍❌По вашему запросу ничего не найдено")

@dp.message(Command("diff"))
async def search_diff(message: Message):
    name = message.text.split()[1:]
    if not name:
        await message.answer("Использование: /diff <easy/medium/hard>")
        return
    recipe = await api.Search_recipe_by_difficulty(name[0])
    if recipe:
        answer = "🍳 Найденные рецепты:\n\n"
        for i, rec in enumerate(recipe, 1):
            answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
        answer += "\n📝 Для просмотра рецепта введите его номер:"
        await message.answer(answer)
        dp.current_user_data = recipe
    else:
        await message.answer("🔍❌По вашему запросу ничего не найдено")

@dp.message(Command("time"))
async def search_time(message: Message):
    time_args = message.text.split()[1:]
    if time_args and time_args[0].isdigit():
        recipe = await api.Search_recipe_by_time(int(time_args[0]))
        if recipe:
            answer = "🍳 Найденные рецепты:\n\n"
            for i, rec in enumerate(recipe, 1):
                answer += f"{i}. {rec['title']} ({rec['cooking_time']} мин.)\n"
            answer += "\n📝 Для просмотра рецепта введите его номер:"
            await message.answer(answer)
            dp.current_user_data = recipe
        else:
            await message.answer("🔍❌По вашему запросу ничего не найдено")


@dp.message(lambda message: message.text.isdigit())
async def select_recipe(message: Message):
    if hasattr(dp, 'current_user_data'):
        recipes = dp.current_user_data
        number = int(message.text)
        if 1 <= number <= len(recipes):
            recipe = recipes[number - 1]
            ingr = ", ".join(recipe['ingredients'])
            text = f"<b>{recipe['title']}</b>\n\n🎯Сложность: {recipe['difficulty']}\n⏱️Время: {recipe['cooking_time']} мин\n🥬Ингредиенты: {ingr}\n📋Инструкция:\n{recipe['instructions']}"
            await message.answer(text, parse_mode=ParseMode.HTML)
        else:
            await message.answer("❌ Неверный номер рецепта")

@dp.message()
async def handle_any(message: Message):
    await message.answer("Неизвестная команда. Пришлите фото продукта или используйте /help")
async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="name", description="По названию"),
        BotCommand(command="product", description="По ингредиентам"),
        BotCommand(command="time", description="По времени"),
        BotCommand(command="diff", description="По сложности")
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main():
    await set_default_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())