import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Just a dummy embeddings since ollama might not be running
class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.1]*768 for _ in texts]
    def embed_query(self, text):
        return [0.1]*768

data_path = "./backend/data/vector_db_test"
os.makedirs(data_path, exist_ok=True)
db = Chroma(persist_directory=data_path, embedding_function=DummyEmbeddings())
docs = db.similarity_search("test", k=1)
print(f"Empty db search result: {docs}")
