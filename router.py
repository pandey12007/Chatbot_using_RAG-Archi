from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from model import IncidentQuery

from vectordb import search_incident


# --------------------------------
# FastAPI App
# --------------------------------

app = FastAPI()


# --------------------------------
# Create Router
# --------------------------------

router = APIRouter(
    prefix="/api",
    tags=["Incident"]
)


# --------------------------------
# Create Database Tables
# --------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------
# Database Dependency
# --------------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# --------------------------------
# Request Model
# --------------------------------

class QueryRequest(BaseModel):

    query: str


# --------------------------------
# Home API
# --------------------------------

@router.get("/")
def home():

    return {
        "message": "Medical Incident RAG API is running"
    }


# --------------------------------
# RAG Search API
# --------------------------------

@router.post("/search")
def search(
    request: QueryRequest,
    db: Session = Depends(get_db)
):

    query = request.query

    if not query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )


    # Search ChromaDB
    results = search_incident(query, 3)

    print("Results:", results)


    # Check result
    if not results["metadatas"]:

        raise HTTPException(
            status_code=404,
            detail="No result found"
        )


    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]


    # Best result
    best_result = metadatas[0]

    print("Best result:", best_result)


    # --------------------------------
    # Save Result Into SQL
    # --------------------------------

    new_query = IncidentQuery(

        query=query,

        incident_id=best_result["incident_id"],

        category=best_result["category"],

        subcategory=best_result["subcategory"],

        severity=best_result["severity"],

        solution=best_result["solution"]

    )


    db.add(new_query)

    db.commit()

    db.refresh(new_query)


    # --------------------------------
    # Response
    # --------------------------------

    return {

        "query": query,

        "best_match": {

            "incident_id": best_result["incident_id"],

            "solution": best_result["solution"],

            "distance": distances[0]

        },

        "saved_to_sql": True,

        "database_id": new_query.id

    }


# --------------------------------
# History API
# --------------------------------

@router.get("/history")
def get_history(
    db: Session = Depends(get_db)
):

    records = db.query(IncidentQuery).all()


    return [

        {

            "id": record.id,

            "query": record.query,

            "incident_id": record.incident_id,

            "category": record.category,

            "subcategory": record.subcategory,

            "severity": record.severity,

            "solution": record.solution

        }

        for record in records

    ]


# --------------------------------
# Include Router
# --------------------------------

app.include_router(router)