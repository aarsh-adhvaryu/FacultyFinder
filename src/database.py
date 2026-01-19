import sqlite3
import os

# --- Configuration (Absolute Paths to prevent directory errors) ---
DB_FOLDER = r"D:\faculty_finder\data"
DB_NAME = "faculty.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)


def init_db():
    """
    Initializes the SQLite database with the required schema.
    Creates the 'data' directory if it does not exist.
    """
    # 1. Ensure the data folder exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"Directory '{DB_FOLDER}' created.")

    # 2. Connect to the database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Enable Foreign Key support (Required for CASCADE DELETE in SQLite)
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 3. Create the 'faculty' table
        # Stores raw and cleaned profile data with a unique constraint on profile_url
        create_faculty_table = """
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            university TEXT DEFAULT 'DA-IICT',
            designation TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            profile_url TEXT UNIQUE,
            hyperlink TEXT,
            education TEXT,
            teaching TEXT,      -- Verified: Column exists
            biography TEXT,
            publications TEXT,
            research_raw TEXT
        );
        """
        cursor.execute(create_faculty_table)

        # 4. Create the 'research_tags' table
        # Implements One-to-Many relationship for fast filtering
        create_tags_table = """
        CREATE TABLE IF NOT EXISTS research_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER,
            tag TEXT,
            FOREIGN KEY (faculty_id) REFERENCES faculty (id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_tags_table)

        conn.commit()
        print(f"Database initialized successfully at: {DB_PATH}")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    init_db()
