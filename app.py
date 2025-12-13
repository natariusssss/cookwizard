import streamlit as st
import requests
import pandas as pd
api_base_url="http://localhost:8000"
search_endpoint="/recipes/search/"
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
    max_time=st.number_input(
        "Максимальное время готовки (мин)",
        min_value=1,
        max_value=120,
        value=60
    )
with col2:
    difficulty=st.selectbox(
        "Сложность",
        options=["Все", "easy", "medium", "hard"],
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
        recipes=response.json()
        if recipes:
            st.success(f"Найдено {len(recipes)} рецептов, соответствующих вашим критериям!")
            df=pd.DataFrame(recipes)
            st.dataframe(
                df[["title", "cooking_time", "difficulty", "ingredients"]],
                use_container_width=True
            )

            st.markdown("---")
            st.subheader("Подробности первого рецепта:")
            first_recipe=recipes[0]
            st.markdown(f"**Название:** {first_recipe['title']}")
            st.markdown(
                f"**Время:** {first_recipe['cooking_time']} мин | **Сложность:** {first_recipe['difficulty'].capitalize()}")
            st.text_area("Инструкции", value=first_recipe['instructions'], height=200, disabled=True)

        else:
            st.warning("Рецепты не найдены по вашим критериям. Попробуйте изменить ингредиенты или фильтры.")

    except requests.exceptions.ConnectionError:
        st.error("Ошибка подключения. Убедитесь, что FastAPI запущен на порту 8000")
    except requests.exceptions.RequestException as e:
        st.error(f"Произошла ошибка при выполнении запроса: {e}")