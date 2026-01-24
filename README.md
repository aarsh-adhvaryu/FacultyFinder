# FacultyFinder: University Faculty Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📌 Project Overview

FacultyFinder is an end-to-end Data Engineering pipeline designed to **scrape, clean, store, and serve** faculty profile data from the DA-IICT university website.

It automates the process of gathering unstructured web data, transforming it into a structured relational schema, and exposing it via a high-performance REST API for downstream applications (like RAG-based search engines or semantic analysis).

---

## 🚀 Key Features

- **Robust Ingestion:** Uses **Scrapy** to crawl multiple pagination layers and faculty categories (Regular, Adjunct, etc.)
- **Data Transformation:** Includes a **Jupyter Notebook** for data quality auditing, text cleaning (HTML stripping), and normalization
- **Structured Storage:** Implements a normalized **SQLite** database schema separating core profiles from research tags (One-to-Many relationship)
- **REST API:** Provides a **FastAPI** service with endpoints for full data retrieval, specific ID lookup, and name-based search

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.9+ |
| **Ingestion** | Scrapy |
| **Processing** | Pandas, NumPy |
| **Storage** | SQLite3 |
| **API** | FastAPI, Uvicorn, Pydantic |

---

## 📂 Project Structure
```text
FacultyFinder/
│
├── api/                       # Serving Layer
│   └── main.py                # FastAPI endpoints
│
├── daiict_scraper/            # Ingestion Layer
│   └── daiict_scraper/
│       ├── spiders/
│       │   └── faculty_spider.py  # Crawling logic
│       └── items.py           # Scrapy data model
│
├── data/                      # Storage Layer
│   ├── raw/                   # Bronze: Raw Scrapy output
│   ├── processed/             # Silver: Cleaned CSVs
│   └── faculty.db             # Gold: Final SQLite Database
│
├── notebooks/                 # Analysis Layer
│   └── Data_cleaning.ipynb    # Data quality & text cleaning
│
├── src/                       # Engineering Scripts
│   ├── database.py            # DB Schema initialization
│   └── migrate.py             # ETL (CSV -> SQLite) script
│
└── requirements.txt           # Dependencies
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/aarsh-adhvaryu/FacultyFinder.git
cd FacultyFinder
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Usage Guide (The Pipeline)

Run these commands in order to execute the full data pipeline.

### Step 1: Ingestion (Scraping)

Crawls the website and saves raw data to `data/raw/`.
```bash
cd daiict_scraper
scrapy crawl faculty_spider -o ../data/raw/faculty_data.csv
cd ..
```

### Step 2: Transformation (Cleaning)

Opens the notebook to audit data and generate the clean CSV.

1. Open Jupyter: `jupyter notebook`
2. Run `notebooks/Data_cleaning.ipynb` (Click "Run All")
3. Output saved to: `data/processed/cleaned_faculty_data.csv`

### Step 3: Storage (Migration)

Loads the clean CSV into the SQLite database.
```bash
python src/migrate.py
```

> **Note:** If you need to reset IDs to 1, delete `data/faculty.db` before running this.

### Step 4: Serving (API)

Starts the local server.
```bash
uvicorn api.main:app --reload --port 8001
```

---

## 📡 API Documentation

Once the server is running, access the interactive Swagger UI at:

**http://127.0.0.1:8001/docs**

### Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/faculty/all` | Retrieve all faculty profiles | N/A |
| `GET` | `/faculty/search` | Search faculty by name | `?name=Gupta` |
| `GET` | `/faculty/{id}` | Get a specific faculty member by ID | `/faculty/1` |

### Example Request
```bash
# Get all faculty
curl http://127.0.0.1:8001/faculty/all

# Search by name
curl http://127.0.0.1:8001/faculty/search?name=Gupta

# Get specific faculty
curl http://127.0.0.1:8001/faculty/1
```

---

## 📊 Database Schema

The project uses a normalized SQLite database (`faculty.db`).

### Tables

**`faculty` Table:**
- Stores name, email, teaching, biography, publications, etc.

**`research_tags` Table:**
- Stores individual research interests linked via `faculty_id`

### Schema Diagram
```
faculty (1) ----< (Many) research_tags
   |                        |
   |- id (PK)              |- id (PK)
   |- name                 |- faculty_id (FK)
   |- email                |- tag
   |- teaching
   |- biography
   |- publications
   └── ...
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is for educational purposes as part of the Data Engineering curriculum.

---

## 👤 Author

**Aarsh Adhvaryu**

- GitHub: [@aarsh-adhvaryu](https://github.com/aarsh-adhvaryu)

---

## 🙏 Acknowledgments

- DA-IICT for providing the data source
- FastAPI and Scrapy communities for excellent documentation

---

**⭐ If you found this project helpful, please consider giving it a star!**