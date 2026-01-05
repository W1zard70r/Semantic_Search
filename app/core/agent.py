import os
import asyncio
from langchain_ollama import ChatOllama
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool # Самый простой способ создания инструментов


from app.core.db import VectorDB
from app.core.engine import SearchEngine

# Создаем инструмент через декоратор 
@tool
def search_in_store(query: str):
    """Ищет товары в базе. Если товаров нет, возвращает сообщение о пустоте."""
    db = VectorDB()
    engine = SearchEngine()
    vec = engine.get_embedding(query)
    results = db.search(vec, limit=2)
    
    if not results:
        return "В БАЗЕ ДАННЫХ НИЧЕГО НЕ НАЙДЕНО. СКАЖИ ПОЛЬЗОВАТЕЛЮ, ЧТО ТОВАРА НЕТ."
        
    return "\n".join([f"НАЙДЕНО: {r['item']['name']}: {r['item']['description']}" for r in results])


class ShopAgent:
    def __init__(self, engine, db): # Принимаем объекты
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.llm = ChatOllama(model="llama3.2", base_url=ollama_url, temperature=0)
        
        # Используем переданные объекты вместо создания новых
        self.engine = engine
        self.db = db
        
        # Список инструментов
        self.tools = [search_in_store]

        # 3. Современный промпт (без лишнего мусора)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Ты — робот-инвентаризатор магазина. 
            ТВОЕ ГЛАВНОЕ ПРАВИЛО: Тебе ЗАПРЕЩЕНО выдумывать товары. 
            У тебя есть доступ ТОЛЬКО к товарам из инструмента поиска.

            Инструкция:
            1. Если пользователь спрашивает о чем-то, ВСЕГДА вызывай search_in_store.
            2. Если инструмент вернул список товаров, перечисли ТОЛЬКО ТЕ, которые в нем есть. 
            3. Если в списке нет подходящих товаров, отвечай строго: 'В нашем ассортименте нет товаров для этого запроса'.
            4. Если пользователь благодарит или здоровается, просто ответь вежливо и коротко.
            5. Никогда не упоминай шампуни, маски или другие предметы, если их нет в результатах поиска.
            6. Отвечай строго на русском языке.
            Ты — профессиональный продавец. Переводи 'extreme' как 'экстремальный спорт', а не как катастрофу."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # 4. Создаем агента (Tool Calling вместо ReAct)
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        
        # 5. Исполнитель
        self.executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, # Оставляем для красоты в консоли
            max_iterations=5
        )

    async def chat(self, user_message: str):
        try:
            result = await self.executor.ainvoke({"input": user_message})
            return result["output"]
        except Exception as e:
            return f"Ошибка агента: {str(e)}"

# Тестовый запуск
if __name__ == "__main__":
    agent = ShopAgent()
    async def main():
        print("\n=== ЗАПУСК АГЕНТА (Tool Calling) ===")
        reply = await agent.chat("Какие у вас есть варианты, чтобы быстро ездить по горам?")
        print(f"\nИТОГ: {reply}")
    
    asyncio.run(main())