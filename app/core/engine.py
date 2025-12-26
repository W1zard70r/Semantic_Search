from sentence_transformers import SentenceTransformer
import numpy as np


class SearchEngine:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    def get_embedding(self, text: str):
        embedding = self.model.encode(text)
        return embedding.tolist()
    
if __name__ == "__main__":
    engine = SearchEngine()
    vec = engine.get_embedding("хочу купить телефон")
    print(f"Размер вектора: {len(vec)}")
    print(f"Первые 5 чисел: {vec[:5]}")
