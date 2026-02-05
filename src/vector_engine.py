import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class FacultyVectorEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
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
            bio = str(doc.get("biography", ""))
            research = str(doc.get("research", ""))
            teaching = str(doc.get("teaching", ""))
            tags = doc.get("research_interests", "")
            if isinstance(tags, list):
                tags = ", ".join([str(t) for t in tags])

            full_text = f"Professor {name}. \nBiography: {bio}\nResearch Areas: {research}\nTeaching: {teaching}\nKeywords: {tags}"
            text_corpus.append(full_text)

        self.corpus_embeddings = self.model.encode(text_corpus, convert_to_tensor=True)
        self.corpus_embeddings = self.corpus_embeddings.cpu().numpy()
        print("✅ Database Vectorized.")

    def search(self, query, top_k=5):
        query_embedding = (
            self.model.encode([query], convert_to_tensor=True).cpu().numpy()
        )
        scores = cosine_similarity(query_embedding, self.corpus_embeddings)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = scores[idx]
            if (
                score > 0.15
            ):  # Lowered threshold slightly to ensure we get everyone relevant
                prof = self.metadata[idx]
                results.append(
                    {
                        "name": prof.get("name"),
                        "score": round(float(score), 4),
                        "tags": prof.get("research_interests"),
                        "email": prof.get("email"),
                        "profile_url": prof.get("profile_url"),
                        # --- ADDED FIELDS FOR UI ---
                        "education": prof.get("education", "Not listed"),
                        "research": prof.get("research", "Not listed"),
                        "publications": prof.get("publications", "Not listed"),
                        "image_url": prof.get("image_url"),
                    }
                )
        return results
