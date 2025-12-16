import streamlit as st
import requests
import pandas as pd
from typing import List, Optional
from collections import Counter
import altair as alt
from datetime import datetime

api_base_url = "http://backend:8000"

st.set_page_config(layout="wide")
st.title("CookWizard: Мастер Рецептов")
st.markdown("---")


@st.cache_data
def get_all_recipes_data() -> List[str]:
    try:
        response = requests.get(f"{api_base_url}/api/recipes")
        response.raise_for_status()
        recipes_data = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Не удалось получить данные для статистики: {e}")
        return []
    if not recipes_data:
        return []
    all_ingredients = []
    for recipe in recipes_data:
        if isinstance(recipe.get('ingredients'), list):
            all_ingredients.extend(recipe.get('ingredients'))

    return all_ingredients


if 'search_history' not in st.session_state:
    st.session_state.search_history = []

tab1, tab2, tab3 = st.tabs(["🔍 Найти рецепты", "📊 Статистика", "📜 История поисков"])

with tab1:
    st.header("Найти рецепт")
    search_type = st.radio(
        "Искать по:",
        ["Ингредиентам", "Названию рецепта", "Ингредиентам и названию"],
        horizontal=True
    )


    if search_type in ["Ингредиентам", "Ингредиентам и названию"]:
        user_ingredients = st.text_input(
            "Введите ингредиенты через запятую",
            value="",
            placeholder="например: курица, картошка, морковь"
        )
    else:
        user_ingredients = ""

    if search_type in ["Названию рецепта", "Ингредиентам и названию"]:
        recipe_title = st.text_input(
            "Введите название рецепта",
            value="",
            placeholder="например: курица с картошкой"
        )
    else:
        recipe_title = ""


    col1, col2 = st.columns(2)
    with col1:
        max_time = st.slider(
            "Максимальное время готовки (мин)",
            min_value=0,
            max_value=180,
            value=60,
            step=5
        )
    with col2:
        difficulty_options = ["Все", "легко", "средне", "сложно"]
        difficulty = st.selectbox(
            "Сложность",
            options=difficulty_options,
            index=0
        )

    if st.button("🔎 Найти рецепты", type="primary"):
        if search_type == "Ингредиентам" and not user_ingredients:
            st.warning("Пожалуйста, введите ингредиенты для поиска")
            st.stop()
        elif search_type == "Названию рецепта" and not recipe_title:
            st.warning("Пожалуйста, введите название рецепта")
            st.stop()
        elif search_type == "Ингредиентам и названию" and not user_ingredients and not recipe_title:
            st.warning("Пожалуйста, введите ингредиенты или название рецепта")
            st.stop()


        params = {}

        if user_ingredients:
            params["ingredients"] = user_ingredients

        if recipe_title:
            params["title"] = recipe_title

        params["max_time"] = max_time

        if difficulty != "Все":
            difficulty_mapping = {
                "легко": "easy",
                "средне": "medium",
                "сложно": "hard"
            }
            params["difficulty"] = difficulty_mapping.get(difficulty, difficulty)

        request_url = f"{api_base_url}/api/search"

        st.info(f"📤 Отправка запроса на: {request_url}")

        try:
            response = requests.get(request_url, params=params)
            response.raise_for_status()
            data = response.json()


            if isinstance(data, list):
                recipes = data
                total_matches = len(recipes)
            else:
                recipes = data.get("recipes", []) if isinstance(data, dict) else []
                total_matches = len(recipes)

            search_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "search_type": search_type,
                "ingredients": user_ingredients,
                "title": recipe_title,
                "max_time": max_time,
                "difficulty": difficulty if difficulty != "Все" else None,
                "found_recipes": total_matches,
                "recipes": recipes[:2] if recipes else []  # Сохраняем первые 2 рецепта
            }

            st.session_state.search_history.insert(0, search_entry)
            if len(st.session_state.search_history) > 20:
                st.session_state.search_history = st.session_state.search_history[:20]

            if recipes:
                st.success(f"✅ Найдено {total_matches} рецептов")
                st.markdown("---")

                for i, recipe in enumerate(recipes):
                    if isinstance(recipe, dict):
                        title = recipe.get("title", f"Рецепт {i + 1}")
                        time = recipe.get("cooking_time", "?")
                        difficulty_val = recipe.get("difficulty", "?")
                    else:
                        title = f"Рецепт {i + 1}"
                        time = "?"
                        difficulty_val = "?"

                    difficulty_display_map = {
                        "easy": "легко",
                        "medium": "средне",
                        "hard": "сложно"
                    }
                    difficulty_display = difficulty_display_map.get(difficulty_val, difficulty_val)

                    header = f"🍳 {title} | ⏱️ {time} мин | 🎯 {difficulty_display}"

                    with st.expander(header):
                        st.markdown(f"**Название:** {title}")
                        st.markdown(f"**Время приготовления:** {time} мин")
                        st.markdown(f"**Сложность:** {difficulty_display}")
                        if isinstance(recipe, dict) and 'ingredients' in recipe:
                            st.markdown("**Ингредиенты:**")
                            for ingredient in recipe['ingredients'][:10]:  # Показываем первые 10
                                st.markdown(f"- {ingredient}")

                            if len(recipe['ingredients']) > 10:
                                st.caption(f"... и ещё {len(recipe['ingredients']) - 10} ингредиентов")
                        instructions = ""
                        if isinstance(recipe, dict):
                            instructions = recipe.get('instructions', 'Инструкции отсутствуют.')

                        st.text_area(
                            "Инструкции",
                            value=instructions,
                            height=150,
                            disabled=True,
                            key=f"instructions_{i}"
                        )

            else:
                st.warning("😕 Рецепты не найдены. Попробуйте изменить параметры поиска.")

        except requests.exceptions.ConnectionError:
            st.error(f"❌ Ошибка подключения. Убедитесь, что сервис 'backend' запущен на {api_base_url}.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Ошибка при выполнении запроса: {e}")
        except Exception as e:
            st.error(f"❌ Неожиданная ошибка: {e}")

with tab2:
    st.header("Статистика по рецептам")
    all_ingredients = get_all_recipes_data()
    if all_ingredients:
        ingredient_counts = Counter(all_ingredients)
        st.subheader("Популярные ингредиенты")
        top_n = 10
        top_ingredients_df = pd.DataFrame(ingredient_counts.most_common(top_n), columns=['Ингредиент', 'Частота'])
        chart = alt.Chart(top_ingredients_df).mark_bar(color='#2659e7').encode(
            x=alt.X('Ингредиент', sort='-y'),
            y='Частота',
            tooltip=['Ингредиент', 'Частота']
        ).properties(
            title=f"Топ {top_n} самых популярных ингредиентов"
        )
        st.altair_chart(chart, use_container_width=True)
        st.markdown("---")
        st.subheader("Облако тегов (Часто используемые продукты)")
        top_tags = ingredient_counts.most_common(30)
        tag_html = ""
        max_count = top_tags[0][1] if top_tags else 1
        for ingredient, count in top_tags:
            font_size = 12 + (count / max_count) * 24
            color_hue = 240 + (count / max_count) * 120
            tag_html += f'<span style="font-size: {font_size:.0f}px; margin: 5px; padding: 3px 6px; display: inline-block; color: hsl({color_hue}, 70%, 50%);">{ingredient.capitalize()}</span>'
        st.markdown(
            f'<div style="border: 1px solid #eee; padding: 15px; border-radius: 5px; text-align: center;">{tag_html}</div>',
            unsafe_allow_html=True)

    else:
        st.warning("Нет данных для отображения статистики. Убедитесь, что база данных заполнена.")

with tab3:
    st.header("📜 История поисков")

    if not st.session_state.search_history:
        st.info("История поиска пуста. Выполните поиск в первой вкладке.")
    else:
        st.write(f"📊 Всего поисков: {len(st.session_state.search_history)}")

        if st.button("🗑️ Очистить историю", type="secondary"):
            st.session_state.search_history = []
            st.rerun()

        for i, search in enumerate(st.session_state.search_history):
            if search['search_type'] == "Ингредиентам":
                search_desc = f"По ингредиентам: {search['ingredients'][:30]}..."
            elif search['search_type'] == "Названию рецепта":
                search_desc = f"По названию: {search['title'][:30]}..."
            else:
                search_desc = f"Комбинированный поиск"

            with st.expander(f"🔍 #{i + 1} - {search_desc} | Найдено: {search['found_recipes']}"):
                st.markdown(f"**⏰ Время:** {search['timestamp']}")
                st.markdown(f"**🔎 Тип поиска:** {search['search_type']}")

                if search['ingredients']:
                    st.markdown(f"**🥦 Ингредиенты:** {search['ingredients']}")

                if search['title']:
                    st.markdown(f"**📝 Название:** {search['title']}")

                st.markdown(f"**⏱️ Макс. время:** {search['max_time']} мин")

                if search['difficulty']:
                    st.markdown(f"**🎯 Сложность:** {search['difficulty']}")

                st.markdown(f"**✅ Найдено рецептов:** {search['found_recipes']}")
                if search['recipes']:
                    st.markdown("**🍳 Примеры найденных рецептов:**")
                    for recipe in search['recipes']:
                        if isinstance(recipe, dict):
                            st.markdown(f"- {recipe.get('title', 'Без названия')}")
