import streamlit as st
import requests
import pandas as pd
from typing import List, Optional
from collections import Counter
import altair as alt
api_base_url = "http://backend:8000"
search_endpoint = "/search"
st.set_page_config(layout="wide")
st.title("CookWizard: Мастер Рецептов")
st.markdown("---")
@st.cache_data
def get_all_recipes_data()->List[str]:
    try:
        response=requests.get(f"{api_base_url}/recipes/")
        response.raise_for_status()
        recipes_data=response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Не удалось получить данные для статистики: {e}")
        return []
    if not recipes_data:
        return []
    all_ingredients=[]
    for recipe in recipes_data:
        if isinstance(recipe.get('ingredients'), list):
            all_ingredients.extend(recipe.get('ingredients'))

    return all_ingredients
tab1, tab2, tab3=st.tabs(["Найдённые рецепты", "Статистика", "История поисков"])
with tab1:
    st.header("Найти рецепт по ингредиентам и фильтрам")
    user_ingredients=st.text_input(
        "Введите ингредиенты через запятую (например: курица, картошка)",
        value=""
    )

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
        difficulty_options=["Все", "легко", "средне", "сложно"]
        difficulty=st.selectbox(
            "Сложность",
            options=difficulty_options,
            index=0
        )
    if st.button("Найти рецепты"):
        if not user_ingredients:
            st.warning("Пожалуйста, введите хотя бы один ингредиент для поиска.")
            st.stop()
        params={
            "ingredients": user_ingredients,
            "max_time": max_time,
            "difficulty": difficulty if difficulty!="Все" else None
        }
        request_url=api_base_url+search_endpoint
        st.info(f"Отправка запроса на: {request_url}")
        try:
            response=requests.get(request_url, params=params)
            response.raise_for_status()
            data=response.json()
            recipes=data.get("recipes", [])
            total_matches=data.get("total_matches", len(recipes))
            if recipes:
                st.success(f"Найдено {total_matches} рецептов, соответствующих вашим критериям")
                st.markdown("---")
                st.subheader("Найденные рецепты:")
                for i, recipe in enumerate(recipes):
                    title=recipe.get("title", f"Рецепт {i + 1}")
                    time=recipe.get("cooking_time", "?")
                    difficulty_val=recipe.get("difficulty", "?").capitalize()
                    header=f" {title} | {time} мин | Сложность: {difficulty_val}"
                    with st.expander(header):
                        st.markdown(f"**Название:** {title}")
                        st.markdown(f"**Время приготовления:** {time} мин")
                        st.markdown(f"**Сложность:** {difficulty_val}")
                        st.text_area(
                            "Инструкции",
                            value=recipe.get('instructions', 'Инструкции отсутствуют.'),
                            height=150,
                            disabled=True
                        )

            else:
                st.warning("Рецепты не найдены по вашим критериям. Попробуйте изменить ингредиенты или фильтры.")

        except requests.exceptions.ConnectionError:
            st.error(f"Ошибка подключения. Убедитесь, что сервис 'backend' запущен на {api_base_url}.")
        except requests.exceptions.RequestException as e:
            st.error(f"Произошла ошибка при выполнении запроса: {e}")
with tab2:
    st.header("Статистика по рецептам")
    all_ingredients=get_all_recipes_data()
    if all_ingredients:
        ingredient_counts=Counter(all_ingredients)
        st.subheader("Популярные ингредиенты")
        top_n=10
        top_ingredients_df=pd.DataFrame(ingredient_counts.most_common(top_n), columns=['Ингредиент', 'Частота'])
        chart=alt.Chart(top_ingredients_df).mark_bar(color='#2659e7').encode(
            x=alt.X('Ингредиент', sort='-y'),
            y='Частота',
            tooltip=['Ингредиент', 'Частота']
        ).properties(
            title=f"Топ {top_n} самых популярных ингредиентов"
        )
        st.altair_chart(chart, use_container_width=True)
        st.markdown("---")
        st.subheader("Облако тегов (Часто используемые продукты)")
        top_tags=ingredient_counts.most_common(30)
        tag_html=""
        max_count=top_tags[0][1] if top_tags else 1
        for ingredient, count in top_tags:
            font_size=12+(count/max_count)*24
            color_hue =240+(count/max_count)*120
            tag_html += f'<span style="font-size: {font_size:.0f}px; margin: 5px; padding: 3px 6px; display: inline-block; color: hsl({color_hue}, 70%, 50%);">{ingredient.capitalize()}</span>'
        st.markdown(
            f'<div style="border: 1px solid #eee; padding: 15px; border-radius: 5px; text-align: center;">{tag_html}</div>',
            unsafe_allow_html=True)

    else:
        st.warning("Нет данных для отображения статистики. Убедитесь, что база данных заполнена.")
with tab3:
    st.header("История поиска")