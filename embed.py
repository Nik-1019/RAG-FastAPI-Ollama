import chromadb
import uuid

client = chromadb.PersistentClient(path="./db")

# Delete and recreate the collection cleanly
try:
    client.delete_collection("docs")
except Exception:
    pass  # collection may not exist yet

collection = client.get_or_create_collection("docs")

with open("k8s.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

documents = []
ids = []

for line in lines:
    documents.append(line)
    ids.append(str(uuid.uuid4()))

collection.add(documents=documents, ids=ids)

print(f"Stored {len(documents)} chunks in Chroma")
