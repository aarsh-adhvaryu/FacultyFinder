import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Logic: Prefer Processed CSV (from notebook), fallback to Raw (from Scrapy)
PROCESSED_CSV = os.path.join(BASE_DIR, "data", "processed", "cleaned_faculty_data.csv")
RAW_CSV = os.path.join(BASE_DIR, "data", "raw", "faculty_data.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")


def migrate():
    csv_path = PROCESSED_CSV if os.path.exists(PROCESSED_CSV) else RAW_CSV

    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV not found at {csv_path}")
        return

    print(f"⚙️  Reading from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)

    # Save to DB (overwrite if exists)
    df.to_sql("faculty", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Database updated at {DB_PATH}")


if __name__ == "__main__":
    migrate()
