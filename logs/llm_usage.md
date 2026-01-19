<h2>1."I am working on the 'FacultyFinder' project. Below is the project specification document.
My Role: I am the Lead Data Engineer.Your Role: You are my coding assistant.
Current Context:
I have analyzed the requirements and decided on the following architecture:

Ingestion: I will use Scrapy (not BeautifulSoup) to handle the pagination and multiple URL targets efficiently.
Storage: I will use SQLite with a normalized schema (separating Faculty info from Research Tags).
Serving: I will use FastAPI for the delivery layer.
Please read the document below, acknowledge the constraints (specifically regarding robots.txt and the sqlite3 requirement), and wait for my specific instruction on the first module. Do not generate full code yet."</h2>

<p>OUTPUT:Understood. I have reviewed the "FacultyFinder" project specifications  and your architectural decisions. I am ready to assist you as your coding partner.
Here is a summary of the context and constraints we are working with:
1. Architecture & Tools
Ingestion: We will use Scrapy to handle the crawling. This is a robust choice for handling the pagination  and multiple targets more efficiently than the suggested requests/BeautifulSoup combo.
Storage: We will use SQLite  to persist the data. As requested, we will design a normalized schema to separate faculty profiles from their specific research tags.
Serving: We will use FastAPI to create the endpoint (/faculty/{id} or /all) for the future data science hand-off.

2. Constraints & Compliance
Robots.txt: Since we are using Scrapy, we will ensure our settings respect the target site's robots.txt file to maintain ethical scraping standards and avoid IP bans. This aligns with the "Code Quality" requirement for robust error handling.
Data Persistence: The pipeline must result in a clean, queryable SQLite database that survives the script execution.
LLM Policy: I acknowledge that our interactions—prompts and responses—must be logged in logs/llm_usage.md.
I am ready for your instructions regarding the first module (Ingestion/Scrapy). How would you like to proceed?</p>
<br>
<br>

<h2>2."Let's start with the Storage Layer.
I have designed the relational schema to comply with the project's requirement for a clean separation between faculty entities and their search tags.Please write a Python script (save it as src/database.py) that initializes a SQLite database at data/faculty.db.

Schema Requirements:
1. Table: faculty
This table will store the raw and cleaned profile data.

Columns:
id (Primary Key, Auto Increment)
name (Text, Not Null)
university (Default 'DA-IICT')
designation, email, phone, address
profile_url (Text, Unique)
hyperlink (for Social/Web links)
education, teaching, biography, publications
research_raw (to store the full research text block)

2. Table: research_tags
This table is for the One-to-Many relationship to allow fast filtering.

Columns:
id (Primary Key)
faculty_id (Foreign Key linked to faculty.id, with Cascade Delete)
tag (The individual specialization keyword)

Please use the sqlite3 library and ensure the script creates the folders if they don't exist."</h2>

<p>OUTPUT:Here is the Python script src/database.py to initialize your storage layer.
This script adheres to your "Storage" requirements and implements the relational structure (Faculty and Research_Tags) outlined in the project recommendations. It uses sqlite3 to ensure data persistence  and includes the necessary directory management to prevent errors during the setup phase.</p>
<p>OUTPUT:
import sqlite3
import os


DB_FOLDER = "data"
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
            teaching TEXT,
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
        print("Tables 'faculty' and 'research_tags' represent the schema.")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
</p>
<br>
<br>
<h2>3. "Moving on to the Ingestion Layer.

I have defined the Scrapy Item schema in items.py as follows:

import scrapy
class FacultyItem(scrapy.Item):
Name = scrapy.Field()
University = scrapy.Field()
Type = scrapy.Field()
Profile_URL = scrapy.Field()
Email_ID = scrapy.Field()
Contact_Number = scrapy.Field()
Address = scrapy.Field()
Hyperlink = scrapy.Field()
Education = scrapy.Field()
Specializations = scrapy.Field()
Biography = scrapy.Field()
Publications = scrapy.Field()
Teaching = scrapy.Field()
Research = scrapy.Field()


**Task:**

Please write the Spider code (`spiders/faculty_spider.py`) to crawl the DA-IICT website.
My Requirements & Logic:
URLs: It must loop through these 5 endpoints and tag the Type accordingly:

  * `https://www.daiict.ac.in/faculty` -\> "Regular Faculty"

  * `https://www.daiict.ac.in/adjunct-faculty` -\> "Adjunct Faculty"

  * (Include International Adjunct, Distinguished, and Professor of Practice)

Selector Logic:
  * The main container for a faculty card is `div.facultyDetails`.
  * **Scenario A:** If a link to a full profile exists (`h2 a::attr(href)`), follow it and scrape the full details.
  * **Scenario B (Fallback):** If no link exists (common for Visiting Faculty), scrape whatever is available on the card itself and mark other fields as "N/A".

Cleaning:
  * Implement a helper function `clean_html` using `w3lib.html.remove_tags` to strip HTML and normalize whitespace.
  * Handle the `Specializations` field carefully: if it's missing on the detailage, try to grab it from the list view (the fallback)."</h2>


<p>OUTPUT:
  Here is the spiders/faculty_spider.py code.

This spider implements the "Ingestion" logic  using Scrapy as requested. It handles the pagination/multiple targets by defining start_requests for the 5 different faculty categories and tagging them accordingly. It also includes the clean_html helper function for the "Transformation" step  and implements the fallback logic for faculty members without full profile pages.

import scrapy
from w3lib.html import remove_tags

from ..items import FacultyItem 

class FacultySpider(scrapy.Spider):
    name = "faculty_spider"
    allowed_domains = ["daiict.ac.in"]
    
    # Mapping URLs to Faculty Types
    start_urls_map = {
        "https://www.daiict.ac.in/faculty": "Regular Faculty",
        "https://www.daiict.ac.in/adjunct-faculty": "Adjunct Faculty",
        "https://www.daiict.ac.in/international-adjunct-faculty": "International Adjunct Faculty",
        "https://www.daiict.ac.in/distinguished-faculty": "Distinguished Faculty",
        "https://www.daiict.ac.in/professor-of-practice": "Professor of Practice"
    }

    def start_requests(self):
        for url, f_type in self.start_urls_map.items():
            yield scrapy.Request(url, callback=self.parse, meta={'faculty_type': f_type})

    def clean_html(self, raw_html):
        """
        Helper to strip HTML tags and normalize whitespace.
        """
        if not raw_html:
            return "N/A"
        # remove_tags strips <tags>, then we strip whitespace/newlines
        text = remove_tags(raw_html).replace('\xa0', ' ').strip()
        return " ".join(text.split()) if text else "N/A"

    def parse(self, response):
        faculty_type = response.meta['faculty_type']
        
        # Iterate over each faculty card container
        for card in response.css('div.facultyDetails'):
            item = FacultyItem()
            
            # Basic Extraction from Card
            item['Name'] = self.clean_html(card.css('h2 a::text').get() or card.css('h2::text').get())
            item['Type'] = faculty_type
            item['University'] = "DA-IICT"
            
            # Extract Specializations (Research Interest) from the card for fallback
            # Usually found in 'p' tags or specifically styled spans in the card
            raw_specialization = card.css('p:contains("Research Interest")::text').get() 
            # If not labeled explicitly, sometimes it's just the paragraph text. 
            # Adjust selector based on specific site structure variations.
            if not raw_specialization:
                 raw_specialization = card.css('p.fac-para::text').get()
            
            item['Specializations'] = self.clean_html(raw_specialization)

            # Check for Profile Link (Scenario A vs B)
            profile_link = card.css('h2 a::attr(href)').get()

            if profile_link:
                # Scenario A: Follow the link
                item['Profile_URL'] = response.urljoin(profile_link)
                request = scrapy.Request(
                    item['Profile_URL'], 
                    callback=self.parse_profile,
                    meta={'item': item} # Pass the partially filled item
                )
                yield request
            else:
                # Scenario B: Scrape card details only
                item['Profile_URL'] = "N/A"
                item['Email_ID'] = self.clean_html(card.css('p:contains("Email")::text').get())
                item['Contact_Number'] = "N/A" # Often not listed on card
                
                # Fill remaining detail fields as N/A
                for field in ['Education', 'Biography', 'Publications', 'Teaching', 'Research', 'Address', 'Hyperlink']:
                    item[field] = "N/A"
                
                yield item

    def parse_profile(self, response):
        item = response.meta['item']
        
        # Helper to extract sections based on headers
        # Note: Selectors here assume standard DA-IICT profile structure (divs with specific classes or h2/h2 headers)
        
        # Extract Bio
        # Example: div with class 'biography' or similar
        item['Biography'] = self.clean_html(response.css('div#biography').get())
        if item['Biography'] == "N/A":
             item['Biography'] = self.clean_html(response.css('div.field-name-field-fac-bio').get())

        # Extract Education
        item['Education'] = self.clean_html(response.css('div#education').get())
        
        # Extract Research (Detailed)
        detail_research = self.clean_html(response.css('div#research_interest').get())
        item['Research'] = detail_research if detail_research != "N/A" else "N/A"

        # Specialization Logic: If detail page has better data, overwrite; else keep list view data
        if detail_research != "N/A" and len(detail_research) > len(item['Specializations']):
             item['Specializations'] = detail_research

        # Extract Contact Info if not on card
        item['Email_ID'] = self.clean_html(response.css('div.field-name-field-email').get())
        item['Contact_Number'] = self.clean_html(response.css('div.field-name-field-phone').get())
        item['Address'] = self.clean_html(response.css('div.field-name-field-office-address').get())
        
        # Extract Tabs content (Publications, Teaching)
        item['Publications'] = self.clean_html(response.css('div#publications').get())
        item['Teaching'] = self.clean_html(response.css('div#teaching').get())
        
        # Extract External Links (Hyperlinks)
        item['Hyperlink'] = response.css('div.field-name-field-website a::attr(href)').get() or "N/A"

        yield item
</p>
<br>
<br>

<h2>4. "I have finished the ingestion layer. Now moving to Transformation & Loading (ETL).
I have already performed the data cleaning analysis in a Jupyter Notebook (notebooks/Data_cleaning.ipynb) which exports a clean file named cleaned_faculty_data.csv.
Task: Please write the migration script (src/migrate.py) to load this clean CSV into our SQLite database.

My Logic Requirements:
Dependency: The script must import init_db from database.py to ensure tables exist.
Clear & Load: It should clear the existing tables (DELETE FROM ...) before inserting to prevent duplicates during testing.

Column Mapping:
Map the CSV column Teaching_Clean to the DB column teaching.
Map Biography_Clean to biography, etc.

Tag Splitting: The Specializations column in the CSV is a comma-separated string. You must split this string in Python and insert multiple rows into the research_tags table for each faculty member."</h2>

<p>OUTPUT:
Here is the src/migrate.py script.

This script manages the ETL (Extract, Transform, Load) "Loading" phase. It clears the existing data to prevent duplication, reads the cleaned CSV using pandas (as suggested in the transformation specs ), and handles the one-to-many relationship logic by splitting the Specializations string into individual rows for the research_tags table.

import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import init_db


DB_PATH = os.path.join("data", "faculty.db")
CSV_PATH = "cleaned_faculty_data.csv" # Assumes file is in project root

def migrate_data():
    """
    Loads data from the cleaned CSV into the SQLite database.
    Handles the One-to-Many logic for research tags.
    """
    
    # 1. Dependency: Ensure the Schema exists
    print("Initializing database schema...")
    init_db()

    # 2. Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found. Please run the cleaning notebook first.")
        return

    # 3. Connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 4. Clear & Load: Clean existing tables
        # Note: Delete child table (tags) first to respect Foreign Keys if CASCADE isn't enabled on connection
        print("Clearing existing data...")
        cursor.execute("DELETE FROM research_tags")
        cursor.execute("DELETE FROM faculty")
        conn.commit()

        # 5. Read CSV
        print(f"Reading data from {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)
        
        # Handle NaN values to prevent SQL errors (replace with empty strings or defaults)
        df = df.fillna("")

        faculty_count = 0
        tags_count = 0

        # 6. Iterate & Insert
        for _, row in df.iterrows():
            
            # Map CSV columns to DB columns
            # Using 'get' for safety, assuming CSV headers match Scrapy Items + 'Clean' suffixes
            faculty_data = (
                row.get("Name"),
                row.get("University", "DA-IICT"),
                row.get("Type"),              # Maps to designation
                row.get("Email_ID"),          # Maps to email
                row.get("Contact_Number"),    # Maps to phone
                row.get("Address"),
                row.get("Profile_URL"),
                row.get("Hyperlink"),
                row.get("Education"),
                row.get("Teaching_Clean"),    # Specific requirement
                row.get("Biography_Clean"),   # Specific requirement
                row.get("Publications"),
                row.get("Research")           # Maps to research_raw
            )

            # Insert into 'faculty' table
            cursor.execute("""
                INSERT INTO faculty (
                    name, university, designation, email, phone, address, 
                    profile_url, hyperlink, education, teaching, biography, 
                    publications, research_raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, faculty_data)

            # Get the auto-generated ID of the new faculty row
            faculty_id = cursor.lastrowid
            faculty_count += 1

            # 7. Tag Splitting logic
            specializations = str(row.get("Specializations", ""))
            
            if specializations and specializations.lower() != "nan":
                # Split string by comma and strip whitespace
                tags = [tag.strip() for tag in specializations.split(',') if tag.strip()]
                
                for tag in tags:
                    cursor.execute("""
                        INSERT INTO research_tags (faculty_id, tag)
                        VALUES (?, ?)
                    """, (faculty_id, tag))
                    tags_count += 1

        conn.commit()
        print("Migration successful!")
        print(f"Inserted {faculty_count} faculty profiles.")
        print(f"Inserted {tags_count} research tags.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_data()
</p>
<br>
<br>
<h2>5. "Final step: The Serving Layer.
I need to expose the faculty.db data via a REST API using FastAPI.
Task: Write the API code (api/main.py) with the following specifications:

1. Data Model (Pydantic): Create a FacultyResponse model that includes ALL the fields we scraped (including teaching, education, contact_number). It must also include a list of strings for research_interests.
2. Endpoints:
GET /faculty/all: Returns the full list of faculty.
GET /faculty/search: Accepts a name query parameter (e.g., ?name=Gupta) and performs a SQL LIKE search to return matching profiles.
3. SQL Logic: Use a helper function to fetch the research_tags for each faculty ID and inject them into the final JSON response.</h2>


<p>OUTPUT:
Here is the api/main.py code.
This script implements the Serving Layer using FastAPI. It includes the Pydantic data model validation, the specific endpoints requested (/all and /search), and the SQL logic to merge the relational data (Faculty + Tags) into a single JSON response for the Data Scientist.

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI(title="FacultyFinder API")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")


class FacultyResponse(BaseModel):
    id: int
    name: str
    university: str
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None # Contact Number
    address: Optional[str] = None
    profile_url: Optional[str] = None
    hyperlink: Optional[str] = None
    education: Optional[str] = None
    teaching: Optional[str] = None
    biography: Optional[str] = None
    publications: Optional[str] = None
    research_raw: Optional[str] = None
    # aggregated list from the research_tags table
    research_interests: List[str] = []


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def get_research_tags(cursor, faculty_id: int) -> List[str]:
    """
    Helper to fetch research tags for a specific faculty ID.
    Performs the join/lookup on the research_tags table.
    """
    query = "SELECT tag FROM research_tags WHERE faculty_id = ?"
    cursor.execute(query, (faculty_id,))
    rows = cursor.fetchall()
    return [row["tag"] for row in rows]

def map_row_to_model(cursor, row) -> FacultyResponse:
    """Helper to convert a DB row into the Pydantic model."""
    tags = get_research_tags(cursor, row["id"])
    
    return FacultyResponse(
        id=row["id"],
        name=row["name"],
        university=row["university"],
        designation=row["designation"],
        email=row["email"],
        phone=row["phone"],
        address=row["address"],
        profile_url=row["profile_url"],
        hyperlink=row["hyperlink"],
        education=row["education"],
        teaching=row["teaching"],
        biography=row["biography"],
        publications=row["publications"],
        research_raw=row["research_raw"],
        research_interests=tags
    )



@app.get("/faculty/all", response_model=List[FacultyResponse])
def get_all_faculty():
    """
    Returns the full list of faculty members with their research tags.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM faculty")
        rows = cursor.fetchall()
        
        results = [map_row_to_model(cursor, row) for row in rows]
        return results
    finally:
        conn.close()

@app.get("/faculty/search", response_model=List[FacultyResponse])
def search_faculty(name: str = Query(..., description="Name of the faculty to search for")):
    """
    Performs a SQL LIKE search on the faculty name.
    Example: /faculty/search?name=Gupta
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # SQL LIKE search with wildcards
        search_term = f"%{name}%"
        cursor.execute("SELECT * FROM faculty WHERE name LIKE ?", (search_term,))
        rows = cursor.fetchall()
        
        if not rows:
            return []
            
        results = [map_row_to_model(cursor, row) for row in rows]
        return results
    finally:
        conn.close()



Your Data Engineering Pipeline is now complete. You have:

Ingestion: A Scrapy spider (spiders/faculty_spider.py) to crawl and extract data.
Storage: A schema script (src/database.py) and a migration script (src/migrate.py) to manage the SQLite database.
Serving: A FastAPI app (api/main.py) to expose the data.</p>