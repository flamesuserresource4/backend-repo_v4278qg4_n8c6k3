import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Evaluation, SmccUser

app = FastAPI(title="SMCC Classroom Evaluation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SMCC Classroom Evaluation Backend Running"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Simple in-API utility for average score (no DB state)
class EvaluationCreateResponse(BaseModel):
    id: str
    overall_score: float

@app.post("/api/evaluations", response_model=EvaluationCreateResponse)
async def create_evaluation(payload: Evaluation):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Calculate overall score (average of criteria)
    scores = [
        payload.teaching_effectiveness,
        payload.classroom_management,
        payload.content_knowledge,
        payload.professionalism,
    ]
    overall = sum(scores) / len(scores)

    doc_id = create_document("evaluation", payload)
    return {"id": doc_id, "overall_score": round(overall, 2)}

class EvaluationQuery(BaseModel):
    teacher_name: Optional[str] = None
    evaluator_role: Optional[str] = None
    term: Optional[str] = None

@app.post("/api/evaluations/search")
async def search_evaluations(query: EvaluationQuery):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_dict = {}
    if query.teacher_name:
        filter_dict["teacher_name"] = query.teacher_name
    if query.evaluator_role:
        filter_dict["evaluator_role"] = query.evaluator_role
    if query.term:
        filter_dict["term"] = query.term

    docs = get_documents("evaluation", filter_dict)

    # Convert ObjectId to string if present
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))

        # compute overall score
        scores = [
            d.get("teaching_effectiveness", 0),
            d.get("classroom_management", 0),
            d.get("content_knowledge", 0),
            d.get("professionalism", 0),
        ]
        try:
            d["overall_score"] = round(sum(scores) / 4, 2)
        except Exception:
            d["overall_score"] = 0

    return {"items": docs}

@app.get("/api/roles")
async def get_roles():
    return {
        "roles": [
            "dean",
            "chairperson",
            "subject coordinator",
            "principal",
            "president",
            "vice president",
            "teacher",
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
