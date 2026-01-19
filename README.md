# FacultyFinder: University Faculty Data Pipeline

## 📌 Project Overview
FacultyFinder is an end-to-end Data Engineering pipeline designed to **scrape, clean, store, and serve** faculty profile data from the DA-IICT university website.

It automates the process of gathering unstructured web data, transforming it into a structured relational schema, and exposing it via a high-performance REST API for downstream applications (like RAG-based search engines or semantic analysis).

## 🚀 Key Features
* **Robust Ingestion:** Uses **Scrapy** to crawl multiple pagination layers and faculty categories (Regular, Adjunct, etc.).
* **Data Transformation:** Includes a **Jupyter Notebook** for data quality auditing, text cleaning (HTML stripping), and normalization.
* **Structured Storage:** Implements a normalized **SQLite** database schema separating core profiles from research tags (One-to-Many relationship).
* **REST API:** Provides a **FastAPI** service with endpoints for full data retrieval, specific ID lookup, and name-based search.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Ingestion:** Scrapy
* **Processing:** Pandas, NumPy
* **Storage:** SQLite3
* **API:** FastAPI, Uvicorn, Pydantic

## 📂 Project Structure
```text
D:\faculty_finder\
│
├── api\                       # Serving Layer
│   └── main.py                # FastAPI endpoints
│
├── daiict_scraper\            # Ingestion Layer
│   └── daiict_scraper\
│       ├── spiders\
│       │   └── faculty_spider.py  # Crawling logic
│       └── items.py           # Scrapy data model
│
├── data\                      # Storage Layer
│   ├── raw\                   # Bronze: Raw Scrapy output
│   ├── processed\             # Silver: Cleaned CSVs
│   └── faculty.db             # Gold: Final SQLite Database
│
├── notebooks\                 # Analysis Layer
│   └── Data_cleaning.ipynb    # Data quality & text cleaning
│
├── src\                       # Engineering Scripts
│   ├── database.py            # DB Schema initialization
│   └── migrate.py             # ETL (CSV -> SQLite) script
│
└── requirements.txt           # Dependencies




Installation & SetupClone the RepositoryBashgit clone [https://github.com/YOUR_USERNAME/FacultyFinder.git](https://github.com/YOUR_USERNAME/FacultyFinder.git)
cd FacultyFinder
Create Virtual EnvironmentBashpython -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Mac/Linux
Install DependenciesBashpip install scrapy pandas fastAPI uvicorn pydantic jupyter

 Usage Guide (The Pipeline)Run these commands in order to execute the full data pipeline.Step 1: Ingestion (Scraping)Crawls the website and saves raw data to data/raw/.Bashcd daiict_scraper
scrapy crawl faculty_spider -o ../data/raw/faculty_data.csv
cd ..
Step 2: Transformation (Cleaning)Opens the notebook to audit data and generate the clean CSV.Open Jupyter: jupyter notebookRun notebooks/Data_cleaning.ipynb (Click "Run All")Output saved to: data/processed/cleaned_faculty_data.csvStep 3: Storage (Migration)Loads the clean CSV into the SQLite database.Bashpython src/migrate.py
Note: If you need to reset IDs to 1, delete data/faculty.db before running this.Step 4: Serving (API)Starts the local server.Bashuvicorn api.main:app --reload --port 8001


 API DocumentationOnce the server is running, access the interactive Swagger UI at:http://127.0.0.1:8001/docsEndpointsMethodEndpointDescriptionExampleGET/faculty/allRetrieve all faculty profiles.N/AGET/faculty/searchSearch faculty by name.?name=GuptaGET/faculty/{id}Get a specific faculty member by ID./faculty/1📊 Database SchemaThe project uses a normalized SQLite database (faculty.db).faculty Table: Stores name, email, teaching, biography, publications, etc.research_tags Table: Stores individual research interests linked via faculty_id.
