import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Market", layout="wide")
st.title("AI Market")

# Вспомогательная функция для безопасного получения данных
def fetch_items():
    try:
        response = requests.get(f"{API_URL}/items", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return None # Бэкенд еще не готов

# Проверяем готовность бэкенда
items = fetch_items()

if items is None:
    st.warning("⏳ Подключаюсь к бэкенду... Модель загружается, это может занять до 30 секунд. Пожалуйста, обновите страницу позже.")
    if st.button("Проверить готовность"):
        st.rerun()
    st.stop() # Останавливаем отрисовку остального интерфейса

# Если данные получены — рисуем вкладки
tab1, tab2, tab3 = st.tabs(["🔍 Поиск и Чат", "➕ Добавить товар", "🛠 Управление"])

with tab1:
    st.header("Умный поиск")
    query = st.text_input("Что вы ищете?")
    
    # Создаем две колонки для кнопок
    col1, col2 = st.columns(2)
    
    with col1:
        search_clicked = st.button("🔍 Найти товары", use_container_width=True)
    with col2:
        ask_clicked = st.button("🤖 Спросить ассистента", use_container_width=True)

    if query:
        if search_clicked:
            res = requests.get(f"{API_URL}/search", params={"q": query}).json()
            if not res['results']:
                st.warning("Ничего не найдено по вашему запросу.")
            else:
                for r in res['results']:
                    with st.expander(f"{r['item']['name']} (Сходство: {r['score']:.2f})"):
                        st.write(r['item']['description'])
        
        if ask_clicked:
            with st.spinner("Агент изучает ассортимент..."):
                res = requests.get(f"{API_URL}/ask", params={"question": query}).json()
                st.chat_message("assistant").write(res['answer'])
    elif search_clicked or ask_clicked:
        st.error("Сначала введите запрос!")


with tab2:
    st.header("Разместить объявление")
    with st.form("add_form"):
        p_id = st.number_input("ID товара", step=1)
        p_name = st.text_input("Название")
        p_desc = st.text_area("Описание")
        if st.form_submit_button("Опубликовать"):
            data = {"id": p_id, "name": p_name, "description": p_desc}
            requests.post(f"{API_URL}/items", json=data)
            st.success("Товар успешно добавлен и проиндексирован!")

with tab3:
    st.header("Список всех товаров")
    if not items:
        st.write("Товаров пока нет.")
    for item in items:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{item['name']}** (ID: {item['id']})")
        if col2.button("Удалить", key=f"del_{item['id']}"):
            requests.delete(f"{API_URL}/items/{item['id']}")
            st.rerun()