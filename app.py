from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
import ollama
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")
logging.info(f"Using model: {MODEL_NAME}")

app = FastAPI()

class QueryRequest(BaseModel):
    q: str

class AddRequest(BaseModel):
    text: str

chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")

@app.post("/query")
def query(request: QueryRequest):
    q = request.q
    logging.info(f"/query asked: {q}")

    results = collection.query(
        query_texts=[q],
        n_results=1
    )

    if not results["documents"] or not results["documents"][0]:
        return {
            "answer": "I do not know. The information is not available in the knowledge base."
        }

    context = results["documents"][0][0]
    logging.info(f"Retrieved context: {context}")

    # deterministic safety guard
    if q.lower() not in context.lower():
        return {
            "answer": "I do not know. The information is not available in the knowledge base."
        }

    prompt = f"""
Context:
{context}

Question:
{q}

Answer using only the context above.
"""

    answer = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt
    )

    return {
        "answer": answer["response"].strip()
    }

@app.post("/add")
def add_knowledge(request: AddRequest):
    import uuid
    doc_id = str(uuid.uuid4())

    collection.add(
        documents=[request.text.strip()],
        ids=[doc_id]
    )

    return {
        "status": "success",
        "message": "Content added to knowledge base",
        "id": doc_id
    }

@app.get("/health")
def health():
    return {"status": "ok"}
