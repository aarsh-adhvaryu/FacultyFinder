import streamlit as st
import sqlite3
import os
import sys
import re

# --- PATH SETUP ---
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


# --- HELPER: Format Publications (Restored!) ---
def format_publications(text):
    if not text or text == "Not listed":
        return "No publications available."

    # 1. BOLD the headers
    text = text.replace("Conference Papers", "\n\n**Conference Papers**\n")
    text = text.replace("Journal Articles", "\n\n**Journal Articles**\n")
    text = text.replace("Books/Book Chapters", "\n\n**Books & Chapters**\n")

    # 2. Add Bullet points for readability
    text = re.sub(r"(\d{4}\.)", r"\1\n\n* ", text)

    # 3. Cleanup messy starts
    if not text.strip().startswith("*") and not text.strip().startswith("**"):
        text = "* " + text

    return text


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
@st.cache_resource
def load_engine():
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM faculty").fetchall()
    conn.close()

    data = [dict(row) for row in rows]

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
                "image_url": item.get("Photo_URL"),
                "publications": item.get("Publications"),  # <--- Loaded here
                "teaching": item.get("Teaching"),
            }
        )

    engine = FacultyVectorEngine()
    engine.fit(formatted_data)
    return engine


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
    query = st.text_area(
        "Describe your research interests:",
        placeholder="Type 'top5' to see only the best matches! (Default shows 15)",
        height=100,
    )

    if st.button("🔍 Find Faculty", type="primary"):
        if not query.strip():
            st.warning("Please enter some text first!")
        else:
            with st.spinner("Analyzing profiles..."):

                # --- MAGIC COMMAND LOGIC ---
                search_limit = 15
                if re.search(r"\btop\s*5\b", query, re.IGNORECASE):
                    search_limit = 5
                    st.toast("⚡ 'Top 5' Mode Activated!")
                # ---------------------------

                results = engine.search(query, top_k=search_limit)

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
                                    bio = prof.get("biography")
                                    if bio and len(bio) > 20:
                                        st.write(bio)
                                    else:
                                        st.write(tags)

                                    # --- RESTORED PUBLICATIONS SECTION ---
                                    st.markdown("#### Selected Publications")
                                    raw_pubs = prof.get("publications", "")
                                    # Use the helper function we defined at the top
                                    clean_pubs = format_publications(raw_pubs)
                                    st.markdown(clean_pubs)
                                    # -------------------------------------
    