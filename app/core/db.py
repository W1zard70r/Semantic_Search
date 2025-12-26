from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class VectorDB:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "products"

    def create_collection(self, vector_size: int):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Коллекция '{self.collection_name}' создана.")

    def upload_data(self, items: list, embeddings : list):
        points = [
            PointStruct(
                id=item['id'],
                vector=emb,
                payload=item
            )
            for item, emb in zip(items, embeddings)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Загружено {len(points)} товаров в базу.")

    def search(self, query_vector: list, limit: int = 3):
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        ).points
        # Вытаскиваем полезные данные (payload) и оценку схожести (score)
        results = []
        for res in search_result:
            results.append({
                "item": res.payload,
                "score": res.score # Насколько текст похож (от 0 до 1)
            })
        return results