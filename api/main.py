from fastapi import FastAPI, HTTPException, Query, Path
import sqlite3
from pydantic import BaseModel
from typing import List, Optional
import os

# --- Configuration ---
# Get the directory where this script (main.py) is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")
app = FastAPI(title="FacultyFinder API")


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


# --- Endpoints ---


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


# --- NEW ENDPOINT HERE ---
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
