from fastapi import FastAPI, Query
from app.core.engine import SearchEngine
from app.core.db import VectorDB
from contextlib import asynccontextmanager

# Создаем глобальные переменные для доступа к модели и БД
engine = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, db
    # Инициализируем компоненты при старте
    engine = SearchEngine()
    db = VectorDB(host="127.0.0.1", port=6333)
    print("Поисковый движок готов!")
    yield

app = FastAPI(title="Semantic Search API", lifespan=lifespan)

@app.get("/search")
async def search_products(q: str = Query(..., description="Текст запроса")):
    # 1. Превращаем запрос пользователя в вектор
    query_vector = engine.get_embedding(q)
    
    # 2. Ищем похожие товары в Qdrant
    results = db.search(query_vector, limit=3)
    
    return {
        "query": q,
        "results": results
    }

@app.get("/ask")
async def ask_assistant(question: str = Query(..., description="Вопрос ассистенту")):
    # 1. RETRIEVAL (Поиск фактов)
    query_vector = engine.get_embedding(question)
    search_results = db.search(query_vector, limit=2)
    
    # Собираем найденную информацию в один текст (контекст)
    context = "\n".join([r['item']['description'] for r in search_results])
    
    # 2. GENERATION (Здесь должна быть LLM)
    # В реальном проекте мы бы отправили context + question в OpenAI или Llama 3
    # Сейчас сымитируем ответ, чтобы показать архитектуру:
    prompt = f"На основе данных: {context}. Ответь на вопрос: {question}"
    
    ai_answer = f"Я нашел для вас варианты. Вот что мне известно: {context}. Что-то из этого вас интересует?"

    return {
        "answer": ai_answer,
        "source_context": context,
        "raw_prompt_to_llm": prompt # Показываем, что мы сформировали промпт!
    }


@app.get("/")
def read_root():
    return {"status": "online", "message": "Semantic search engine is running"}