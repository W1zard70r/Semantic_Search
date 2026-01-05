import json
from pathlib import Path
from core.engine import SearchEngine
from core.db import VectorDB


def run_indexing():
    current_dir = Path(__file__).parent.parent
    data_path = current_dir / "data" / "items.json"

    with open(data_path , "r", encoding="utf-8") as f:
        items = json.load(f)
    print("json загружен")
    engine = SearchEngine()
    db = VectorDB()

    print("Генерация эмбеддингов для связки Название + Описание...")
    full_texts = [f"{item['name']}: {item['description']}" for item in items]
    embeddings = [engine.get_embedding(text) for text in full_texts]

    print("embeddings созданы")
    db.create_collection(vector_size=384)
    db.upload_data(items, embeddings)

if __name__ == "__main__":
    run_indexing()