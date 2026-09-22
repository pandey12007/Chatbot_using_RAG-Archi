import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------
# Load CSV
# --------------------------------

csv_file_path = r""

df = pd.read_csv(csv_file_path)

print("CSV loaded successfully")
print(df.head())
print("Total records:", len(df))


# --------------------------------
# Load Embedding Model
# --------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# Create ChromaDB
# --------------------------------

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="Medical_incident_database"
)


# --------------------------------
# Create Documents
# --------------------------------

documents = df["description"].astype(str).tolist()


# --------------------------------
# Create Embeddings
# --------------------------------

embeddings = model.encode(
    documents
).tolist()


# --------------------------------
# Create IDs
# --------------------------------

ids = df["incident_id"].astype(str).tolist()


# --------------------------------
# Create Metadata
# --------------------------------

metadatas = []

for _, row in df.iterrows():

    metadatas.append({

        "incident_id": str(row["incident_id"]),

        "category": str(row["category"]),

        "subcategory": str(row["subcategory"]),

        "severity": str(row["severity"]),

        "solution": str(row["solution"])

    })


# --------------------------------
# Check Lengths
# --------------------------------

print("IDs:", len(ids))

print("Documents:", len(documents))

print("Embeddings:", len(embeddings))

print("Metadata:", len(metadatas))


# --------------------------------
# Add To ChromaDB
# --------------------------------

collection.add(

    ids=ids,

    documents=documents,

    embeddings=embeddings,

    metadatas=metadatas

)


print("500 records successfully added to ChromaDB")

# SEARCH FUNCTION
# --------------------------------

def search_incident(query, top_k=3):

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results
