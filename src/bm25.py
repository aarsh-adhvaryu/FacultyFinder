import math
import re
import json
import os
import numpy as np
from collections import Counter

# --- 1. The Cleaning Layer ---
STOP_WORDS = {
    "vol",
    "pp",
    "page",
    "pages",
    "volume",
    "issue",
    "no",
    "doi",
    "org",
    "international",
    "conference",
    "journal",
    "proceedings",
    "transactions",
    "university",
    "institute",
    "technology",
    "da",
    "iict",
    "daiict",
    "gandhinagar",
    "gujarat",
    "india",
    "new",
    "delhi",
    "ahmedabad",
    "bangalore",
    "meet",
    "prof",
    "professor",
    "dr",
    "mr",
    "mrs",
    "miss",
    "assistant",
    "associate",
    "email",
    "contact",
    "address",
    "phone",
    "mobile",
    "fax",
    "amp",
    "research",
    "interests",
    "and",
    "the",
    "of",
    "in",
    "to",
    "for",
    "with",
    "on",
    "at",
    "by",
    "from",
    "specialization",
    "areas",  # Added these to clean headers
}

# --- 2. The Smart Ontology (Knowledge Graph) ---
# This bridges the gap. "Sound" -> "Signal Processing". "DL" -> "ML".
DOMAIN_KNOWLEDGE = {
    "deep learning": [
        "machine learning",
        "neural networks",
        "cnn",
        "rnn",
        "transformer",
        "llm",
        "computer vision",
        "nlp",
        "artificial intelligence",
    ],
    "machine learning": [
        "deep learning",
        "ai",
        "data science",
        "pattern recognition",
        "predictive modeling",
        "recommendation systems",
        "multimodality",
        "machine learning",
    ],
    "ai": [
        "artificial intelligence",
        "machine learning",
        "reasoning",
        "knowledge graph",
        "autonomous",
        "agent",
        "robotics",
    ],
    "nlp": [
        "natural language processing",
        "text mining",
        "linguistics",
        "speech",
        "sentiment analysis",
        "llm",
        "bert",
        "language models",
    ],
    "sound": ["audio", "speech", "signal processing", "acoustics", "music"],
    "speech": ["asr", "audio", "speaker", "signal processing", "voice", "sound"],
    "data science": [
        "data mining",
        "big data",
        "analytics",
        "applied machine learning",
        "visualization",
        "information retrieval",
        "database",
    ],
    "embedded": ["vlsi", "fpga", "iot", "sensor", "circuit", "hardware"],
    "robotics": ["control", "automation", "mechatronics", "autonomous", "drones"],
}


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|doi\S+|\S+@\S+", "", text)
    text = re.sub(r"meet prof\.? \w+ \w+", "", text)
    text = re.sub(r"&amp;", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    return words


def expand_query_with_domain_knowledge(query_str):
    query_lower = query_str.lower()
    tokens = query_lower.split()
    expanded_tokens = tokens.copy()

    # Bidirectional Check
    for concept, synonyms in DOMAIN_KNOWLEDGE.items():
        # 1. If user searches "Sound", add "Signal Processing"
        if concept in query_lower:
            expanded_tokens.extend(synonyms)

    return " ".join(expanded_tokens)


# --- 3. The Engine ---
class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.metadata = []

    def fit(self, raw_documents):
        print(f"⚙️  Indexing {len(raw_documents)} profiles...")
        self.metadata = raw_documents
        self.corpus = []
        self.doc_len = []
        self.doc_freqs = []
        self.idf = {}
        total_length = 0

        for doc in raw_documents:
            # 1. HARVEST EVERYTHING
            # We now grab 'research' and 'education' too, just in case keywords are hiding there.
            bio = str(doc.get("biography", ""))
            pubs = str(doc.get("publications", ""))
            res_raw = str(doc.get("research", ""))  # Often holds 'Specialization' text
            edu = str(doc.get("education", ""))

            tags = doc.get("research_interests", "")
            if isinstance(tags, list):
                tags = " ".join([str(t) for t in tags])
            else:
                tags = str(tags)

            # Weighting: Tags get 3x, Research Raw gets 2x (it's dense)
            full_text = f"{bio} {pubs} {res_raw} {res_raw} {edu} {tags} {tags} {tags}"

            # 2. Tokenize
            tokens = clean_text(full_text)
            self.corpus.append(tokens)

            # 3. Stats
            length = len(tokens)
            self.doc_len.append(length)
            total_length += length
            freqs = Counter(tokens)
            self.doc_freqs.append(freqs)
            for token in freqs:
                self.idf[token] = self.idf.get(token, 0) + 1

        self.corpus_size = len(self.corpus)
        self.avgdl = total_length / self.corpus_size if self.corpus_size > 0 else 0

        for word, freq in self.idf.items():
            self.idf[word] = math.log(
                1 + (self.corpus_size - freq + 0.5) / (freq + 0.5)
            )

        print("✅ Index built successfully.")

    def get_score(self, query_tokens, index):
        score = 0.0
        doc_freqs = self.doc_freqs[index]
        doc_len = self.doc_len[index]
        for token in query_tokens:
            if token not in doc_freqs:
                continue
            freq = doc_freqs[token]
            idf = self.idf.get(token, 0)
            numerator = idf * freq * (self.k1 + 1)
            denominator = freq + self.k1 * (
                1 - self.b + self.b * (doc_len / self.avgdl)
            )
            score += numerator / denominator
        return score

    def search_with_refinement(self, query_str, top_k=5):
        # 1. Expand (Deep Learning -> Machine Learning)
        expanded_query = expand_query_with_domain_knowledge(query_str)
        query_tokens = clean_text(expanded_query)

        # 2. Search
        scores = [self.get_score(query_tokens, i) for i in range(self.corpus_size)]
        if not any(scores):
            return []

        # 3. Refine (Grab keywords from the winner to find similar people)
        best_idx = np.argmax(scores)
        winner_tokens = self.corpus[best_idx]
        most_common = Counter(winner_tokens).most_common(5)

        refined_tokens = query_tokens.copy()
        for word, count in most_common:
            if word not in refined_tokens:
                refined_tokens.append(word)

        # 4. Final Rank
        final_scores = [
            self.get_score(refined_tokens, i) for i in range(self.corpus_size)
        ]
        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if final_scores[idx] > 0:
                results.append(
                    {
                        "name": self.metadata[idx].get("name"),
                        "score": round(final_scores[idx], 4),
                        # Fallback if tags are empty, grab the first 50 chars of bio
                        "tags": self.metadata[idx].get("research_interests")
                        or str(self.metadata[idx].get("biography", ""))[:100] + "...",
                        "profile_url": self.metadata[idx].get("profile_url"),
                        "email": self.metadata[idx].get("email"),
                    }
                )
        return results


if __name__ == "__main__":
    # Test Block
    possible_paths = ["data/response_1770110808513.json", "response_1770110808513.json"]
    data_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        engine = BM25()
        engine.fit(data)

        # TEST: This should now find Dr. Rana (ML) even if we search "Deep Learning"
        q = "deep learning"
        print(f"\n🔎 Testing: '{q}'")
        for hit in engine.search_with_refinement(q):
            print(f"[{hit['score']}] {hit['name']} -- {hit['tags']}")
