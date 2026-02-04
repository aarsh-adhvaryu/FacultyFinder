from fastapi import FastAPI, HTTPException, Query, Path
import sqlite3
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import json

# --- Configuration ---
# Get the directory where this script (main.py) is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")

# Add the project root to python path so we can import 'src'
sys.path.append(BASE_DIR)

# Import our custom Data Science Engine
try:
    from src.bm25 import BM25
except ImportError:
    print("⚠️ Warning: Could not import BM25. Make sure src/bm25.py exists.")
    BM25 = None

app = FastAPI(
    title="FacultyFinder API",
    description="Hybrid API: SQL for Data Retrieval + Probabilistic AI for Recommendations",
    version="2.0"
)

# --- Global State for ML Model ---
recommendation_engine = None

# --- Data Models ---
class FacultyResponse(BaseModel):
    id: int
    name: str
    university: Optional[str] = "DA-IICT"
    designation: Optional[str]
    email: Optional[str]
    contact_number: Optional[str]
    address: Optional[str]
    hyperlink: Optional[str]
    profile_url: Optional[str]
    education: Optional[str]
    teaching: Optional[str]
    biography: Optional[str]
    publications: Optional[str]
    research: Optional[str]
    research_interests: List[str]

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

# --- Startup Event (The "Brain" Loader) ---
@app.on_event("startup")
def load_ml_model():
    global recommendation_engine
    
    if BM25 is None:
        print("❌ BM25 Module missing. Recommendations will fail.")
        return

    # Smart Path Finding for the JSON Data
    # We look in multiple places to ensure Docker/Local compatibility
    possible_paths = [
        os.path.join(BASE_DIR, "data", "response_1770110808513.json"),
        os.path.join("data", "response_1770110808513.json"),
        "response_1770110808513.json"
    ]
    
    data_path = None
    for path in possible_paths:
        if os.path.exists(path):
            data_path = path
            break
            
    if not data_path:
        print(f"⚠️ Warning: Knowledge Base JSON not found. Recommender will be inactive.")
        print(f"   Checked locations: {possible_paths}")
        return

    print(f"⚙️  Loading Knowledge Base from: {data_path}")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Initialize and Train the Engine
        recommendation_engine = BM25()
        recommendation_engine.fit(data)
        print("✅ Recommender System Online.")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

# --- Database Helpers ---
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

def format_faculty(row, cursor):
    """Helper to format a single DB row into the response dict"""
    cursor.execute("SELECT tag FROM research_tags WHERE faculty_id = ?", (row["id"],))
    tags = [t["tag"] for t in cursor.fetchall()]

    return {
        "id": row["id"],
        "name": row["name"],
        "university": row["university"],
        "designation": row["designation"],
        "email": row["email"],
        "contact_number": row["phone"],
        "address": row["address"],
        "hyperlink": row["hyperlink"],
        "profile_url": row["profile_url"],
        "education": row["education"],
        "teaching": row["teaching"],
        "biography": row["biography"],
        "publications": row["publications"],
        "research": row["research_raw"],
        "research_interests": tags,
    }

# --- Original Endpoints (SQL) ---

@app.get("/faculty/all", response_model=List[FacultyResponse])
def get_all_faculty():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    results = [format_faculty(row, cursor) for row in cursor.fetchall()]
    conn.close()
    return results

@app.get("/faculty/search", response_model=List[FacultyResponse])
def search_faculty(name: str = Query(..., description="Name to search")):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty WHERE name LIKE ?", (f"%{name}%",))
    results = [format_faculty(row, cursor) for row in cursor.fetchall()]
    conn.close()
    return results

@app.get("/faculty/{faculty_id}", response_model=FacultyResponse)
def get_faculty_by_id(
    faculty_id: int = Path(..., description="The ID of the faculty member")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch specific row by ID
    cursor.execute("SELECT * FROM faculty WHERE id = ?", (faculty_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"Faculty with ID {faculty_id} not found"
        )

    result = format_faculty(row, cursor)
    conn.close()
    return result

# --- New AI Endpoint (Probabilistic Search) ---

@app.post("/recommend")
def get_recommendations(request: QueryRequest):
    """
    Intelligent Search using BM25 + Pseudo-Relevance Feedback.
    Finds faculty based on research interests and biography context.
    """
    if not recommendation_engine:
        raise HTTPException(
            status_code=503, 
            detail="Recommender engine is not ready (Model not loaded)."
        )
    
    # Run the "Smart" Search
    results = recommendation_engine.search_with_refinement(request.query, request.top_k)
    
    if not results:
        return {"message": "No relevant faculty found. Try broader keywords.", "results": []}
    
    return {
        "query": request.query,
        "results": results
    }

@app.get("/")
def health_check():
    status = "online" if recommendation_engine else "offline"
    return {
        "status": "running", 
        "recommender_system": status,
        "algorithm": "BM25 + Pseudo-Relevance Feedback"
    }