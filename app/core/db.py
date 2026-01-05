import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class VectorDB:
    def __init__(self):
        # Берем хост из окружения (в докере будет 'qdrant')
        host = os.getenv("QDRANT_HOST", "127.0.0.1")
        self.client = QdrantClient(host=host, port=6333)
        
        self.collection_name = "products"

    def create_collection(self, vector_size: int):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Коллекция '{self.collection_name}' создана.")

    def upload_data(self, items: list, embeddings: list):
        points = [
            PointStruct(
                id=item["id"], 
                vector=emb, 
                payload=item
            )
            for item, emb in zip(items, embeddings)
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: list, limit: int = 3):
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        ).points
        
        results = []
        for res in search_result:
            # ДОБАВЬ ЭТОТ ПРИНТ:
            print(f"[DEBUG DATABASE] Товар: {res.payload.get('name')}, Score: {res.score}")
            
            # if res.score < 0.3: # Оставим пока низкий порог для теста
            #     continue
                
            results.append({
                "item": res.payload,
                "score": res.score
            })
        return results
