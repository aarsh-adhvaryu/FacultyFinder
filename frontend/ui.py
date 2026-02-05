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
st.markdown(
    """
<style>
    .stApp { background-color: #0e1117; }
    .highlight { color: #00ffa3; font-weight: bold; }
    img { border-radius: 8px; }
</style>
""",
    unsafe_allow_html=True,
)


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
        formatted_data.append(
            {
                "name": item.get("Name"),
                "biography": item.get("Biography"),
                "research_interests": item.get("Specializations")
                or item.get("Research"),
                "education": item.get("Education"),
                "email": item.get("Email_ID"),
                "profile_url": item.get("Profile_URL"),
                "image_url": item.get("Photo_URL"),  # <--- CRITICAL
                "publications": item.get("Publications"),
                "teaching": item.get("Teaching"),
            }
        )

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
    st.error(
        f"⚠️ Database not found at `{DB_PATH}`. Please run `src/migrate.py` locally and push `faculty.db` to GitHub."
    )
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
                                img = prof.get("image_url")
                                if img and img.startswith("http"):
                                    st.image(img, width=120)
                                else:
                                    st.image(
                                        "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                                        width=120,
                                    )

                                st.caption(f"✅ Score: {prof.get('score'):.4f}")
                                if prof.get("profile_url"):
                                    st.link_button(
                                        "🌐 Visit Profile", prof["profile_url"]
                                    )

                            with col_info:
                                st.subheader(f"{rank}. {prof['name']}")
                                st.markdown(
                                    f"**🎓 Education:** {prof.get('education', 'N/A')}"
                                )

                                tags = prof.get("tags", "")
                                if tags:
                                    st.markdown(f"**🔬 Interests:** {tags}")

                                if prof.get("email"):
                                    st.markdown(f"📧 `{prof.get('email')}`")

                                with st.expander("📖 View Details"):
                                    st.markdown("#### Research Focus")
                                    # Fallback logic
                                    bio = prof.get("biography")
                                    if bio and len(bio) > 20:
                                        st.write(bio)
                                    else:
                                        st.write(tags)
