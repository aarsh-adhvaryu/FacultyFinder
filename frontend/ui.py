import streamlit as st
import requests

# Configuration
API_URL = "http://127.0.0.1:8000/recommend"

# 1. Page Setup
st.set_page_config(page_title="FacultyFinder AI", page_icon="🎓")

# 2. Header Section
st.title("🎓 FacultyFinder AI")
st.markdown("### Find the perfect mentor for your research.")
st.markdown("*(Powered by Probabilistic BM25 Search)*")

# 3. Input Section (The "Newbie Friendly" part)
# No JSON formatting needed here! Just natural language.
query = st.text_area(
    "Describe what you want to work on:",
    placeholder="e.g., I am interested in deep learning and applying it to medical imaging...",
)

# 4. Search Logic
if st.button("🔍 Find Faculty"):
    if not query.strip():
        st.warning("Please enter some text first!")
    else:
        with st.spinner("Analyzing research profiles..."):
            try:
                # Call your FastAPI Backend
                payload = {"query": query, "top_k": 5}
                response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])

                    if not results:
                        st.info("No direct matches found. Try broader terms.")
                    else:
                        st.success(f"Found {len(results)} matches!")

                        # 5. Display Results nicely
                        for rank, prof in enumerate(results, 1):
                            # Create a clean "Card" for each result
                            with st.container():
                                st.subheader(f"{rank}. {prof['name']}")
                                st.caption(f"Relevance Score: {prof['score']}")

                                # Show tags as colorful badges
                                tags = prof.get("tags", [])
                                if isinstance(tags, list):
                                    st.write(" **Interests:** " + ", ".join(tags[:10]))
                                else:
                                    st.write(f"**Interests:** {tags}")

                                # Add a 'View Profile' button (if URL exists)
                                if prof.get("profile_url"):
                                    st.markdown(
                                        f"[View Profile]({prof['profile_url']})"
                                    )

                                st.markdown("---")  # Divider line
                else:
                    st.error(f"Error: API returned {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the Backend. Is 'uvicorn' running?")
