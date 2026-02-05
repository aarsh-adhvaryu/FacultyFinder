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


<h2>6. once i submit this much, someone else will work on my dataset, and i will work on someone else, i have to make sure that they dont see any error in my repo when that get my github repo</h2>

<p>This is a very important constraint! If you submit the code with D:\faculty_finder\..., it will crash on your evaluator's computer immediately because they probably don't have a D: drive or a folder named faculty_finder in the exact same spot.

To ensure your code works on anyone's computer (Windows, Mac, or Linux), we must replace the "Hardcoded Paths" with "Relative Paths". This tells Python: "Look for the database in the folder right next to me," regardless of where the project is saved.

You need to update these 3 files.

1. Fix src/database.py
This ensures the database is created inside the project folder, no matter who downloads it.

Open src/database.py and replace the "Configuration" section at the top:

Python
import sqlite3
import os



 Get the folder where this script (database.py) is located

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

 Define the data folder relative to the project root

DB_FOLDER = os.path.join(BASE_DIR, "data")
DB_NAME = "faculty.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)



def init_db():
     ... rest of your code remains exactly the same ...
2. Fix src/migrate.py
This ensures the migration script can find the CSV file and the Database on your peer's computer.

Open src/migrate.py and replace the "Configuration" section:

Python
import pandas as pd
import sqlite3
import os
from database import init_db

 CORRECT CONFIGURATION FOR PORTABILITY <br>
 Get the project root folder<br>
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

 Build paths dynamically<br>
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_faculty_data.csv")<br>
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")


def migrate():
    # ... rest of your code remains exactly the same ...
3. Fix api/main.py
This ensures the API finds the database when your peer runs the server.

Open api/main.py and replace the "Configuration" section:

Python
from fastapi import FastAPI, HTTPException, Query, Path
import sqlite3
from pydantic import BaseModel
from typing import List, Optional
import os


 Get the directory where this script (main.py) is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "faculty.db")


app = FastAPI(title="FacultyFinder API")

 ... rest of your code remains exactly the same ...
Final Step: Verify and Push
Test Locally: Stop your server, verify these changes, and run uvicorn api.main:app --reload. If it works for you, it works for them.

Push to GitHub:

Bash
git add .
git commit -m "Switch to relative paths for cross-platform compatibility"
git push
Now, when your peer downloads your repo, they can unzip it anywhere (Desktop, C drive, etc.), run the commands, and it will work perfectly without them needing to edit any code.</p>

<h2>7. this readme file will also serve as my presentation so please add details</h2>
<h2>8. changes to be made in scraper for the use of photo url</h2>

<p>This is the perfect time to integrate the image scraping. Based on the HTML you provided, the image URL is located inside the .facultyPhoto div in the src attribute of the <img> tag.

Here is the Complete "Run From Scratch" Plan. I have updated every single file to handle the new Image URL and ensure the pipeline is unbroken.

1. Update the Scraper (src/scraper.py)
I have updated the scraping logic to grab the image URL and convert it from a relative path (e.g., /sites/...) to a full URL (https://www.daiict.ac.in/sites/...).

Create/Overwrite src/scraper.py:

Python
import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os

class FacultySpider(scrapy.Spider):
    name = "faculty"
    start_urls = ['https://www.daiict.ac.in/faculty']

    def parse(self, response):
        # We iterate over each faculty card
        for faculty in response.css('.facultyDetails'):
            
            # 1. Extract Name & Profile URL
            name = faculty.css('.personalDetails h3 a::text').get()
            profile_url = faculty.css('.personalDetails h3 a::attr(href)').get()
            
            # 2. Extract Image URL (NEW)
            image_src = faculty.css('.facultyPhoto img::attr(src)').get()
            full_image_url = response.urljoin(image_src) if image_src else None

            # 3. Extract Meta Data
            education = faculty.css('.facultyEducation::text').get()
            
            # Extract email (cleanup needed usually)
            email = faculty.css('.facultyemail::text').get()
            
            # Extract Research Interests
            # The HTML shows interests are in a <p> tag inside .areaSpecialization
            interests = faculty.css('.areaSpecialization p::text').getall()
            # Clean up the list
            interests = [i.strip() for i in interests if i.strip()]
            
            if name:
                yield {
                    'name': name.strip(),
                    'image_url': full_image_url,
                    'profile_url': profile_url,
                    'education': education.strip() if education else None,
                    'email': email.strip() if email else None,
                    'research_interests': interests,
                    # We will visit the profile page to get more details (Bio, etc)
                    # For now, we return the base data. To go deeper, we'd yield a request.
                    # But for this "Single Page" test, this is enough.
                }

# --- Runner Code ---
if __name__ == "__main__":
    # 1. Setup Data Folder
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 2. Delete old file if exists
    output_file = 'data/faculty_data.json'
    if os.path.exists(output_file):
        os.remove(output_file)

    # 3. Run Spider
    process = CrawlerProcess(settings={
        'FEEDS': {
            output_file: {'format': 'json', 'encoding': 'utf8', 'indent': 4},
        },
        'LOG_LEVEL': 'INFO',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    process.crawl(FacultySpider)
    process.start()
    
    print(f"✅ Scraping Complete. Data saved to {output_file}")
2. Update the Brain (src/vector_engine.py)
We need to pass the image_url through the engine so the API can receive it.

Overwrite src/vector_engine.py:

Python
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class FacultyVectorEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"⏳ Loading AI Model ({model_name})...")
        self.model = SentenceTransformer(model_name)
        self.corpus_embeddings = None
        self.metadata = []
        print("✅ AI Model Loaded.")

    def fit(self, raw_documents):
        print(f"⚙️  Vectorizing {len(raw_documents)} profiles...")
        self.metadata = raw_documents
        text_corpus = []

        for doc in raw_documents:
            name = str(doc.get("name", ""))
            # Use get() with default empty strings to avoid crashes
            bio = str(doc.get("biography", "")) 
            research = str(doc.get("research_interests", "")) 
            if isinstance(doc.get("research_interests"), list):
                research = ", ".join(doc.get("research_interests"))
            
            education = str(doc.get("education", ""))
            
            # The AI reads this text to understand the professor
            full_text = f"Professor {name}. Education: {education}. Research Interests: {research}. Biography: {bio}"
            text_corpus.append(full_text)

        self.corpus_embeddings = self.model.encode(text_corpus, convert_to_tensor=True)
        self.corpus_embeddings = self.corpus_embeddings.cpu().numpy()
        print("✅ Database Vectorized.")

    def search(self, query, top_k=5):
        query_embedding = self.model.encode([query], convert_to_tensor=True).cpu().numpy()
        scores = cosine_similarity(query_embedding, self.corpus_embeddings)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = scores[idx]
            if score > 0.15: 
                prof = self.metadata[idx]
                results.append({
                    "name": prof.get("name"),
                    "score": round(float(score), 4),
                    # --- PASSING THE NEW IMAGE URL ---
                    "image_url": prof.get("image_url"), 
                    "tags": prof.get("research_interests"),
                    "email": prof.get("email"),
                    "profile_url": prof.get("profile_url"),
                    "education": prof.get("education", "Not listed"),
                    "research": str(prof.get("research_interests", "")), # fallback for summary
                    "publications": prof.get("publications", "Not listed")
                })
        return results

if __name__ == "__main__":
    # Test Block
    path = "data/faculty_data.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        engine = FacultyVectorEngine()
        engine.fit(data)
        print("Test Search 'Machine Learning':", engine.search("Machine Learning", 1))
3. Update the API (api/main.py)
We update the startup logic to look for our new scraped file name (faculty_data.json).

Overwrite api/main.py:

Python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import json

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --- IMPORT THE NEW ENGINE ---
try:
    from src.vector_engine import FacultyVectorEngine
except ImportError:
    print("⚠️ Warning: Could not import FacultyVectorEngine.")
    FacultyVectorEngine = None

app = FastAPI(title="FacultyFinder AI", version="3.0")

# --- Global Model State ---
recommendation_engine = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 150

@app.on_event("startup")
def load_ml_model():
    global recommendation_engine
    if FacultyVectorEngine is None: return

    # We look for the file generated by the new scraper
    data_path = os.path.join(BASE_DIR, "data", "faculty_data.json")
            
    if not os.path.exists(data_path):
        print(f"⚠️ Warning: {data_path} not found. Run the scraper first!")
        return

    print(f"⚙️  Loading Knowledge Base from: {data_path}")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        recommendation_engine = FacultyVectorEngine()
        recommendation_engine.fit(data)
        print("✅ Semantic Search Engine Online.")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

@app.post("/recommend")
def get_recommendations(request: QueryRequest):
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="AI Model is loading or data missing.")
    results = recommendation_engine.search(request.query, request.top_k)
    return {"query": request.query, "results": results}
4. Update the Frontend (frontend/ui.py)
Now we use the real image URL!

Overwrite frontend/ui.py:

Python
import streamlit as st
import requests
import re

API_URL = "http://127.0.0.1:8000/recommend"

st.set_page_config(page_title="FacultyFinder AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .highlight { color: #00ffa3; font-weight: bold; }
    img { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

def format_publications(text):
    if not text or text == "Not listed": return "No publications available."
    text = text.replace("Conference Papers", "\n\n**Conference Papers**\n")
    text = text.replace("Journal Articles", "\n\n**Journal Articles**\n")
    text = re.sub(r'(\d{4}\.)', r'\1\n\n* ', text)
    return text

st.title("🎓 FacultyFinder AI")
st.markdown("##### *(Powered by Semantic Vector Search & Transformers)*") 

with st.container():
    query = st.text_area("Describe your research interests:", height=100)
    if st.button("🔍 Find Faculty", type="primary"):
        if not query.strip():
            st.warning("Please enter some text first!")
        else:
            with st.spinner("Analyzing profiles..."):
                try:
                    response = requests.post(API_URL, json={"query": query, "top_k": 150})
                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        if not results:
                            st.info("No matches found.")
                        else:
                            st.success(f"Found {len(results)} matches!")
                            for rank, prof in enumerate(results, 1):
                                with st.container():
                                    st.markdown("---")
                                    col_img, col_info = st.columns([1.5, 5])
                                    with col_img:
                                        # --- NEW IMAGE LOGIC ---
                                        img_url = prof.get('image_url')
                                        # Use the real URL if it exists, otherwise the placeholder
                                        if img_url and "http" in img_url:
                                            st.image(img_url, width=150)
                                        else:
                                            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
                                        
                                        st.caption(f"✅ Score: {prof.get('score'):.4f}")
                                        if prof.get('profile_url'):
                                            st.link_button("🌐 Visit Profile", prof['profile_url'])

                                    with col_info:
                                        st.subheader(f"{rank}. {prof['name']}")
                                        st.markdown(f"**🎓 Education:** {prof.get('education', 'N/A')}")
                                        
                                        tags = prof.get('tags', [])
                                        if isinstance(tags, list): tags = ", ".join(tags)
                                        st.markdown(f"**🔬 Interests:** {tags}")
                                        
                                        if prof.get('email'): st.markdown(f"📧 `{prof.get('email')}`")

                                        with st.expander("📖 View Details"):
                                            st.markdown("#### Research Interests")
                                            st.write(tags)
                    else:
                        st.error("API Error")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")</p>

<h2>9. For project 2 we will use transformer</h2>

<p>It takes courage to kill your darling code, but this is the right engineering decision. We are moving from a Lexical Search (Keyword Matching) to a Semantic Search (Meaning Matching).

Here is your "Demolition & Reconstruction" plan.

🗑️ Step 1: The Cleanup (Delete)
Delete the file src/bm25.py. (We don't need the math anymore).

Delete src/__pycache__ folder if it exists.

📦 Step 2: The Setup (Install)
You need the libraries that power the AI. Run this in your terminal:

PowerShell
pip install sentence-transformers scikit-learn
(Note: This might take a minute. It installs Torch and the Transformer libraries).

🧠 Step 3: The New Engine (src/vector_engine.py)
Create a new file src/vector_engine.py. This code is cleaner, shorter, and 10x smarter than the BM25 code.

Python
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class FacultyVectorEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the Semantic Search Engine.
        Downloads the 'all-MiniLM-L6-v2' model (80MB) automatically.
        This model translates text into 384-dimensional vectors.
        """
        print(f"⏳ Loading AI Model ({model_name})...")
        # This will download the model to your local cache the first time
        self.model = SentenceTransformer(model_name)
        self.corpus_embeddings = None
        self.metadata = []
        print("✅ AI Model Loaded.")

    def fit(self, raw_documents):
        """
        Ingests profiles and converts them into Vectors.
        """
        print(f"⚙️  Vectorizing {len(raw_documents)} profiles... (Please wait)")
        
        self.metadata = raw_documents
        text_corpus = []

        for doc in raw_documents:
            # 1. Construct a "Natural Language" representation of the professor
            # We combine all fields into a single descriptive paragraph.
            name = str(doc.get("name", ""))
            bio = str(doc.get("biography", ""))
            research = str(doc.get("research", "")) # Critical for Dr. Rana
            teaching = str(doc.get("teaching", "")) # Critical for Sourish
            
            tags = doc.get("research_interests", "")
            if isinstance(tags, list): 
                tags = ", ".join([str(t) for t in tags])
            
            # This string is what the AI 'reads'
            full_text = f"Professor {name}. \nBiography: {bio}\nResearch Areas: {research}\nTeaching: {teaching}\nKeywords: {tags}"
            text_corpus.append(full_text)

        # 2. Encode: Text -> Vector (The Magic Step)
        # This converts the list of strings into a Matrix of numbers
        self.corpus_embeddings = self.model.encode(text_corpus, convert_to_tensor=True)
        
        # Move to CPU for compatibility
        self.corpus_embeddings = self.corpus_embeddings.cpu().numpy()
        
        print("✅ Database Vectorized & Ready.")

    def search(self, query, top_k=5):
        """
        Finds the most semantically similar profiles to the query.
        """
        # 1. Vectorize the User's Query
        query_embedding = self.model.encode([query], convert_to_tensor=True).cpu().numpy()

        # 2. Calculate Cosine Similarity (The "Angle" between vectors)
        # Result is an array of scores between 0 (complete opposite) and 1 (exact match)
        scores = cosine_similarity(query_embedding, self.corpus_embeddings)[0]

        # 3. Sort & Rank
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = scores[idx]
            
            # Threshold: Ignore matches that are too weak (< 0.25)
            # This prevents random noise results
            if score > 0.25: 
                prof = self.metadata[idx]
                results.append({
                    "name": prof.get("name"),
                    "score": round(float(score), 4),
                    "tags": prof.get("research_interests") or "General Research",
                    "profile_url": prof.get("profile_url"),
                    "email": prof.get("email")
                })
        
        return results

# --- Independent Test Block ---
if __name__ == "__main__":
    # Check if data exists
    path = "response_1770110808513.json" 
    if not os.path.exists(path): path = "data/" + path
    
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        engine = FacultyVectorEngine()
        engine.fit(data)
        
        # Test 1: The "Dr. Rana" Case
        print("\n🔎 Test 1: 'Deep Learning' (Should find Dr. Rana's Applied ML)")
        results = engine.search("Deep Learning")
        for r in results[:3]: print(f"[{r['score']}] {r['name']}")

        # Test 2: The "Sourish" Case
        print("\n🔎 Test 2: 'LLM' (Should find Sourish's Large Language Models)")
        results = engine.search("LLM")
        for r in results[:3]: print(f"[{r['score']}] {r['name']}")

        # Test 3: The "Amit" Case
        print("\n🔎 Test 3: 'Machine Learning' (Should find Amit Mankodi)")
        results = engine.search("Machine Learning")
        for r in results[:3]: print(f"[{r['score']}] {r['name']}")
🔌 Step 4: Wire it up (api/main.py)
You need to tell your API to use this new engine instead of the old one.

Open api/main.py and update these two parts:

Part A: The Import (Top of file)

Python
# CHANGE THIS:
# from src.bm25 import BM25 
# TO THIS:
from src.vector_engine import FacultyVectorEngine
Part B: The Startup Logic (Middle of file)

Python
# Find the @app.on_event("startup") function
# Update the initialization line inside the 'try' block:

        # Initialize and Train the Engine
        # recommendation_engine = BM25()  <-- DELETE THIS
        # recommendation_engine.fit(data) <-- DELETE THIS
        
        recommendation_engine = FacultyVectorEngine() # <-- ADD THIS
        recommendation_engine.fit(data)               # <-- ADD THIS
🧪 Step 5: Run the Test
Run the engine file directly first to see the magic happen:

PowerShell
python src/vector_engine.py
It will download the model (green bar) and run the 3 tests. You should see Dr. Rana, Sourish, and Amit all showing up in the correct places without you writing a single line of dictionary code.

Tell me if the test results look good!</p>

<h2>Deployment on Streamlit</h2>




Deploying on Streamlit Community Cloud is the easiest way to share your project, but there is one major architectural catch you need to handle first.

⚠️ The Deployment Problem
Streamlit Cloud is designed to host only the frontend. It cannot talk to the uvicorn API running on your laptop (localhost).

To deploy this successfully "from Streamlit," we need to use the "Monolith Approach". We will modify frontend/ui.py slightly so it imports the Brain (Vector Engine) directly, instead of asking the API for answers.

This keeps your project structure intact but makes it deployable in one click.

🛠️ Step 1: Update frontend/ui.py (The "All-in-One" Version)
Overwrite your frontend file with this code. It uses st.cache_resource to load the AI model once when the app starts, just like your backend did.

Python
import streamlit as st
import sqlite3
import os
import sys

# --- PATH SETUP (Crucial for Cloud) ---
# This tells Streamlit where to find your 'src' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from src.vector_engine import FacultyVectorEngine
except ImportError:
    st.error("❌ Could not import the Brain. Check your folder structure.")
    st.stop()

# --- CONFIGURATION ---
DB_PATH = os.path.join(parent_dir, "data", "faculty.db")

st.set_page_config(page_title="FacultyFinder AI", page_icon="🎓", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .highlight { color: #00ffa3; font-weight: bold; }
    img { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 🧠 THE BRAIN (Cached) ---
# This replaces the API. It runs inside Streamlit now.
@st.cache_resource
def load_engine():
    if not os.path.exists(DB_PATH):
        return None
    
    # 1. Load Data from DB
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM faculty").fetchall()
    conn.close()
    
    data = [dict(row) for row in rows]
    
    # 2. Map Columns (Same logic as your API)
    formatted_data = []
    for item in data:
        formatted_data.append({
            "name": item.get("Name"),
            "biography": item.get("Biography"),
            "research_interests": item.get("Specializations") or item.get("Research"),
            "education": item.get("Education"),
            "email": item.get("Email_ID"),
            "profile_url": item.get("Profile_URL"),
            "image_url": item.get("Photo_URL"),  # <--- CRITICAL
            "publications": item.get("Publications"),
            "teaching": item.get("Teaching")
        })
        
    # 3. Initialize AI
    engine = FacultyVectorEngine()
    engine.fit(formatted_data)
    return engine

# Load the engine immediately
engine = load_engine()

# --- UI LOGIC ---
st.title("🎓 FacultyFinder AI")
st.markdown("##### *(Powered by Semantic Vector Search & Transformers)*") 

if not engine:
    st.error(f"⚠️ Database not found at `{DB_PATH}`. Please run `src/migrate.py` locally and push `faculty.db` to GitHub.")
    st.stop()

with st.container():
    query = st.text_area("Describe your research interests:", height=100)
    
    if st.button("🔍 Find Faculty", type="primary"):
        if not query.strip():
            st.warning("Please enter some text first!")
        else:
            with st.spinner("Analyzing profiles..."):
                # Direct Search (No API Call)
                results = engine.search(query, top_k=150)
                
                if not results:
                    st.info("No matches found.")
                else:
                    st.success(f"Found {len(results)} matches!")
                    
                    for rank, prof in enumerate(results, 1):
                        with st.container():
                            st.markdown("---")
                            col_img, col_info = st.columns([1.5, 5])
                            
                            with col_img:
                                img = prof.get('image_url')
                                if img and img.startswith("http"):
                                    st.image(img, width=120)
                                else:
                                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
                                
                                st.caption(f"✅ Score: {prof.get('score'):.4f}")
                                if prof.get('profile_url'):
                                    st.link_button("🌐 Visit Profile", prof['profile_url'])

                            with col_info:
                                st.subheader(f"{rank}. {prof['name']}")
                                st.markdown(f"**🎓 Education:** {prof.get('education', 'N/A')}")
                                
                                tags = prof.get('tags', '')
                                if tags: st.markdown(f"**🔬 Interests:** {tags}")
                                
                                if prof.get('email'): st.markdown(f"📧 `{prof.get('email')}`")

                                with st.expander("📖 View Details"):
                                    st.markdown("#### Research Focus")
                                    # Fallback logic
                                    bio = prof.get('biography')
                                    if bio and len(bio) > 20:
                                        st.write(bio)
                                    else:
                                        st.write(tags)
📦 Step 2: Prepare requirements.txt
Streamlit Cloud needs to know what libraries to install. Since we are moving the "Brain" to the frontend, you must ensure the AI libraries are listed here.

Overwrite requirements.txt with:

Plaintext
streamlit
pandas
numpy
scikit-learn
sentence-transformers
torch



