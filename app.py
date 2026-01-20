import os
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

# Mock LLM mode for CI testing
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "0") == "1"

if not USE_MOCK_LLM:
    import ollama

app = FastAPI()

class QueryRequest(BaseModel):
    q: str

chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")

@app.post("/query")
def query(request: QueryRequest):
    q = request.q
    results = collection.query(query_texts=[q], n_results=1)
    
    if not results["documents"] or not results["documents"][0]:
        return {"answer": "I do not know. The information is not available in the knowledge base."}
    
    context = results["documents"][0][0]
    
    # Deterministic safety guard - check if key terms from question are in context
    stop_words = {'what', 'is', 'are', 'how', 'why', 'when', 'where', 'who', 'which', 'the', 'a', 'an'}
    question_words = [word.lower().strip('?.,!') for word in q.split() 
                     if len(word) > 3 and word.lower() not in stop_words]
    context_lower = context.lower()
    
    # All meaningful words from the question should be in the context
    if question_words and not all(word in context_lower for word in question_words):
        return {"answer": "I do not know. The information is not available in the knowledge base."}

    if USE_MOCK_LLM:
        return {"answer": context}

    answer = ollama.generate(
        model="tinyllama",
        prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer using only the context above."
    )

    return {"answer": answer["response"].strip()}
