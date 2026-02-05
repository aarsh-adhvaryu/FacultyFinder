from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import sys

# Setup Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")

# Import Vector Engine
try:
    from src.vector_engine import FacultyVectorEngine
except ImportError:
    FacultyVectorEngine = None

app = FastAPI(title="FacultyFinder AI", version="3.0")
recommendation_engine = None


class QueryRequest(BaseModel):
    query: str
    top_k: int = 150


@app.on_event("startup")
def load_ml_model():
    global recommendation_engine
    if not FacultyVectorEngine:
        return

    if not os.path.exists(DB_PATH):
        print(f"⚠️ Warning: Database not found at {DB_PATH}. Run migrate.py!")
        return

    print("⚙️  Loading data from SQLite Database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM faculty").fetchall()
        conn.close()

        # Convert DB Rows to Dictionary List
        data = [dict(row) for row in rows]

        # Map DB Columns to what the Engine/UI expects
        formatted_data = []
        for item in data:
            formatted_data.append(
                {
                    "name": item.get("Name"),
                    "biography": item.get("Biography"),
                    # Fallback logic for interests
                    "research_interests": item.get("Specializations")
                    or item.get("Research"),
                    "education": item.get("Education"),
                    "email": item.get("Email_ID"),
                    "profile_url": item.get("Profile_URL"),
                    # --- THE CRITICAL MAP ---
                    # Maps DB column 'Photo_URL' to API key 'image_url'
                    "image_url": item.get("Photo_URL"),
                    "publications": item.get("Publications"),
                    "teaching": item.get("Teaching"),
                }
            )

        recommendation_engine = FacultyVectorEngine()
        recommendation_engine.fit(formatted_data)
        print("✅ Semantic Search Engine Online.")

    except Exception as e:
        print(f"❌ Failed to load model: {e}")


@app.post("/recommend")
def get_recommendations(request: QueryRequest):
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="AI Model loading or DB missing.")
    results = recommendation_engine.search(request.query, request.top_k)
    return {"results": results}
