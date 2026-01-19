import pandas as pd
import sqlite3
import os
from database import init_db

# Configuration
CSV_PATH = r"D:\faculty_finder\data\processed\cleaned_faculty_data.csv"
DB_PATH = r"D:\faculty_finder\data\faculty.db"


def migrate():
    print("--- Starting Migration (v3: Fix Column Mapping) ---")

    if not os.path.exists(CSV_PATH):
        print(f"Error: Processed data not found at {CSV_PATH}")
        print("Make sure you ran the Jupyter Notebook to generate the CSV!")
        return

    # 1. Initialize DB (Ensures tables exist)
    init_db()

    # 2. Load Data
    df = pd.read_csv(CSV_PATH)
    # Convert NaN to None for SQLite
    df = df.where(pd.notnull(df), None)

    print(f"Loaded {len(df)} records from CSV.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear old data to prevent duplicates
    cursor.execute("DELETE FROM research_tags")
    cursor.execute("DELETE FROM faculty")

    inserted_count = 0

    for index, row in df.iterrows():
        try:
            cursor.execute(
                """
                INSERT INTO faculty (
                    name, university, designation, email, phone, 
                    address, profile_url, hyperlink, education, 
                    teaching, biography, publications, research_raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    row.get("Name"),
                    row.get("University", "DA-IICT"),
                    row.get("Type"),
                    row.get("Email_ID"),
                    row.get("Contact_Number"),
                    row.get("Address"),
                    row.get("Profile_URL"),
                    row.get("Hyperlink"),
                    row.get("Education"),
                    # --- FIX IS HERE ---
                    row.get(
                        "Teaching_Clean"
                    ),  # Changed from "Teaching" to "Teaching_Clean"
                    # -------------------
                    row.get("Biography_Clean"),
                    row.get("Publications_Clean"),
                    row.get("Research_Clean"),
                ),
            )

            faculty_id = cursor.lastrowid

            # Insert Tags
            specs = row.get("Specializations")
            if specs and specs is not None:
                tags = [t.strip() for t in str(specs).split(",") if t.strip()]
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO research_tags (faculty_id, tag) VALUES (?, ?)",
                        (faculty_id, tag),
                    )

            inserted_count += 1

        except Exception as e:
            print(f"Error on row {index}: {e}")

    conn.commit()
    conn.close()
    print(f"--- Complete. Inserted {inserted_count} profiles. ---")


if __name__ == "__main__":
    migrate()
