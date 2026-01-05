from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from app.core.engine import SearchEngine
from app.core.db import VectorDB
from app.core.agent import ShopAgent # Импортируем нашего агента
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, db, agent
    engine = SearchEngine()
    db = VectorDB() 
    
    # Передаем существующие объекты в агента
    agent = ShopAgent(engine=engine, db=db) 
    
    print("🚀 Поисковый движок и AI-агент готовы!")
    yield

app = FastAPI(title="Semantic Search & AI Agent API", lifespan=lifespan)

@app.get("/search")
async def search_products(q: str = Query(..., description="Текст запроса")):
    """
    Классический семантический поиск. 
    Возвращает список самых похожих товаров из базы.
    """
    query_vector = engine.get_embedding(q)
    results = db.search(query_vector, limit=3)
    return {
        "query": q,
        "results": results
    }

@app.get("/ask")
async def ask_assistant(question: str = Query(..., description="Вопрос ассистенту")):
    """
    Интеллектуальный помощник (Агент).
    Сам решает, когда искать в базе, и формулирует ответ на русском языке.
    """
    # Теперь просто вызываем метод чата у агента
    ai_response = await agent.chat(question)
    
    return {
        "question": question,
        "answer": ai_response
    }

@app.get("/")
def read_root():
    return {
        "status": "online", 
        "endpoints": ["/search", "/ask", "/docs"]
    }

class Product(BaseModel):
    id: int
    name: str
    description: str

# Добавляем в существующий main.py:

@app.post("/items")
async def add_product(product: Product):
    """Добавить новый товар в базу и сразу его проиндексировать"""
    try:
        # 1. Генерируем вектор
        vector = engine.get_embedding(product.description)
        # 2. Сохраняем в Qdrant
        db.upload_data([product.model_dump()], [vector])
        return {"status": "success", "message": f"Товар '{product.name}' добавлен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items")
async def list_products():
    """Показать все товары, которые сейчас есть в поиске"""
    # В Qdrant это делается через метод scroll
    points, _ = db.client.scroll(collection_name=db.collection_name, limit=100)
    return [p.payload for p in points]

@app.delete("/items/{item_id}")
async def delete_product(item_id: int):
    """Удалить товар из базы"""
    db.client.delete(
        collection_name=db.collection_name,
        points_selector=[item_id]
    )
    return {"status": "success", "message": f"Товар {item_id} удален"}