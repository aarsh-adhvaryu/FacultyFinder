import pandas as pd
import re
import os
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "faculty_data.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_faculty_data.csv")

def clean_text(text):
    if pd.isna(text) or text == "N/A":
        return "Not listed"
    # Remove HTML artifacts and extra spaces
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text

def run_cleaning():
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Error: Raw data not found at {RAW_DATA_PATH}")
        return

    print("⚙️  Cleaning Data...")
    df = pd.read_csv(RAW_DATA_PATH)

    # 1. Clean Text Columns
    text_cols = ["Biography", "Publications", "Research", "Teaching", "Education"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # 2. FILL MISSING IMAGES
    # If Photo_URL is missing/NaN, fill with empty string
    if "Photo_URL" not in df.columns:
        df["Photo_URL"] = ""
    df["Photo_URL"] = df["Photo_URL"].fillna("")

    # 3. SELECT COLUMNS (The Fix)
    # We explicitly include Photo_URL here
    keep_cols = [
        "Name", "University", "Type", "Designation", 
        "Email_ID", "Contact_Number", "Address", 
        "Hyperlink", "Profile_URL", "Photo_URL",  # <--- CRITICAL
        "Education", "Specializations", 
        "Biography", "Publications", "Research", "Teaching"
    ]
    
    # Only keep columns that actually exist in the raw data
    final_cols = [c for c in keep_cols if c in df.columns]
    df_clean = df[final_cols]

    # 4. Save
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df_clean.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"✅ Data Cleaned & Saved. Records: {len(df_clean)}")

if __name__ == "__main__":
    run_cleaning()