import streamlit as st
import requests
import re

# Configuration
API_URL = "http://127.0.0.1:8000/recommend"

# 1. Page Configuration
st.set_page_config(page_title="FacultyFinder AI", page_icon="🎓", layout="wide")

# Custom CSS
st.markdown(
    """
<style>
    .stApp { background-color: #0e1117; }
    .profile-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41444e;
        margin-bottom: 20px;
    }
    .highlight { color: #00ffa3; font-weight: bold; }
    .pub-text { font-size: 0.9em; color: #e0e0e0; }
</style>
""",
    unsafe_allow_html=True,
)


# --- HELPER: Fix the "Haywire" Text ---
def format_publications(text):
    if not text or text == "Not listed":
        return "No publications available."

    # 1. BOLD the headers (Conference Papers, Journal Articles)
    text = text.replace("Conference Papers", "\n\n**Conference Papers**\n")
    text = text.replace("Journal Articles", "\n\n**Journal Articles**\n")
    text = text.replace("Books/Book Chapters", "\n\n**Books & Chapters**\n")

    # 2. Add Bullet points for readability
    # Heuristic: If we see a year (20xx) followed by a dot, it's likely the end of a citation.
    # We add a double newline to force spacing.
    text = re.sub(r"(\d{4}\.)", r"\1\n\n* ", text)

    # 3. Cleanup messy starts
    if not text.strip().startswith("*") and not text.strip().startswith("**"):
        text = "* " + text

    return text


# --- HELPER: Get Initials for Avatar ---
def get_initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}"
    return name[:2]


# 2. Header
st.title("🎓 FacultyFinder AI")
st.markdown("##### *(Powered by Semantic Vector Search & Transformers)*")

# 3. Input Section
with st.container():
    query = st.text_area(
        "Describe your research interests:",
        placeholder="e.g., I want to work on deep learning, specifically dealing with medical images...",
        height=100,
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        search_btn = st.button("🔍 Find Faculty", type="primary")

# 4. Search Logic
if search_btn:
    if not query.strip():
        st.warning("Please enter some text first!")
    else:
        with st.spinner("Analyzing faculty profiles..."):
            try:
                payload = {"query": query, "top_k": 150}
                response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])

                    if not results:
                        st.info("No matches found.")
                    else:
                        st.success(f"Found {len(results)} matches!")

                        for rank, prof in enumerate(results, 1):
                            with st.container():
                                st.markdown("---")
                                col_img, col_info = st.columns([1.5, 5])

                                with col_img:
                                    # 📸 IMAGE LOGIC - Use actual photo URL from API
                                    photo_url = prof.get("image_url", "")

                                    # DEBUG: Show what URL we're trying to load
                                    # st.caption(f"🔗 {photo_url}")  # Uncomment to debug

                                    # Use real photo if available, otherwise use placeholder
                                    if (
                                        photo_url
                                        and photo_url != "N/A"
                                        and photo_url.startswith("http")
                                    ):
                                        try:
                                            # Try loading the image with explicit error handling
                                            st.image(
                                                photo_url,
                                                width=100,
                                                use_container_width=False,
                                            )
                                        except Exception as e:
                                            # If image fails to load, show placeholder
                                            st.image(
                                                "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                                                width=100,
                                            )
                                            st.caption("⚠️ Image unavailable")
                                    else:
                                        # Fallback to placeholder avatar
                                        st.image(
                                            "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                                            width=100,
                                        )
                                    score = float(prof.get("score", 0))
                                    if score > 0.35:
                                        st.markdown(
                                            f"🔥 <span class='highlight'>Top Match ({score:.4f})</span>",
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        st.caption(f"✅ Score: {score:.4f}")

                                    if prof.get("profile_url"):
                                        st.link_button(
                                            "🌐 Visit Profile", prof["profile_url"]
                                        )

                                with col_info:
                                    st.subheader(f"{rank}. {prof['name']}")

                                    # Education
                                    edu = prof.get("education", "Not listed")
                                    if edu and edu != "Not listed":
                                        st.markdown(f"**🎓 Education:** {edu}")

                                    # Interests
                                    tags = prof.get("tags", "")
                                    if tags:
                                        st.markdown(f"**🔬 Interests:** {tags}")

                                    # Email
                                    email = prof.get("email")
                                    if email:
                                        st.markdown(f"📧 `{email}`")

                                    # 📚 FORMATTED PUBLICATIONS
                                    with st.expander("📖 View Research & Publications"):
                                        st.markdown("#### Research Summary")
                                        research_summary = prof.get("research", "")
                                        research_interests = prof.get("tags", "")

                                        if (
                                            research_summary
                                            and len(str(research_summary)) > 20
                                            and research_summary != "Not listed"
                                        ):
                                            st.write(research_summary)
                                        elif research_interests:
                                            # Show interests as bullet points if summary is missing
                                            if isinstance(research_interests, str):
                                                research_interests = (
                                                    research_interests.split(",")
                                                )
                                            for tag in research_interests:
                                                st.markdown(f"* {tag.strip()}")
                                        else:
                                            st.info(
                                                "No detailed research summary available."
                                            )
                                        # ---------------------------

                                        st.markdown("#### Selected Publications")
                                        raw_pubs = prof.get("publications", "")
                                        clean_pubs = format_publications(raw_pubs)
                                        st.markdown(clean_pubs)

                else:
                    st.error(f"Error: API returned {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the Backend. Is 'uvicorn' running?")
