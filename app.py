import streamlit as st
import requests
import pandas as pd
api_base_url="http://backend:8000"
search_endpoint="/search"
st.set_page_config(layout="centered")
st.title("CookWizard: Мастер Рецептов")
st.markdown("---")
st.header("Найти рецепт по ингредиентам")
user_ingredients=st.text_input(
    "Введите ингредиенты через запятую (например: курица, картошка)",
    value=""
)
col1, col2=st.columns(2)
with col1:
    max_time=st.slider(
        "Максимальное время готовки (мин)",
        min_value=0,
        max_value=180,
        value=60,
        step=5
    )
with col2:
    difficulty_options = ["Все", "легко", "средне", "сложно"]
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
    try:
        response=requests.get(api_base_url+search_endpoint, params=params)
        response.raise_for_status()
        data=response.json()
        recipes=data.get("recipes", [])
        total_matches=data.get("total_matches", len(recipes))
        if recipes:
            st.success(f"Найдено {total_matches} рецептов, соответствующих вашим критериям!")
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
        st.error("Ошибка подключения. Убедитесь, что FastAPI запущен на порту 8000")
    except requests.exceptions.RequestException as e:
        st.error(f"Произошла ошибка при выполнении запроса: {e}")