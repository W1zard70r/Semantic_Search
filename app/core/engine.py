from sentence_transformers import SentenceTransformer
import numpy as np


class SearchEngine:
    def __init__(self):
        model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        print(f"🔥 ЗАГРУЗКА МОДЕЛИ: {model_name}")
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: str):
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
if __name__ == "__main__":
    engine = SearchEngine()
    vec = engine.get_embedding("хочу купить телефон")
    print(f"Размер вектора: {len(vec)}")
    print(f"Первые 5 чисел: {vec[:5]}")
