"""
RAHI Embedding Service
=======================
Converts text into vector embeddings for semantic search.

Model: all-MiniLM-L6-v2
  - 384 dimensional vectors
  - Runs completely locally (no API key needed)
  - Fast: ~1000 sentences/second on CPU
  - Size: ~80MB download (one time)

Why local embeddings?
  - No API cost, no quota limits
  - Works offline
  - Data stays on your machine (privacy)
  - Good enough quality for RAHI's needs

Research connection:
  Sentence-BERT paper: Reimers & Gurevych, 2019
  https://arxiv.org/abs/1908.10084
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# Global model instance — loaded once, reused
_model = None
EMBEDDING_DIM = 384   # all-MiniLM-L6-v2 output dimension


def get_model() -> SentenceTransformer:
    """Lazy load the model — only downloads/loads when first called."""
    global _model
    if _model is None:
        print("🔄 Loading embedding model (first time may take a moment)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded!")
    return _model


def embed_text(text: str) -> list[float]:
    """
    Convert a single text string into a vector embedding.

    Args:
        text: Any string (sentence, paragraph, question)

    Returns:
        List of 384 floats representing the semantic meaning
    """
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple texts at once — more efficient than one by one.

    Args:
        texts: List of strings

    Returns:
        List of embeddings (one per text)
    """
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate similarity between two vectors.
    Returns: 0.0 (completely different) to 1.0 (identical meaning)
    """
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ── Quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔢 Testing RAHI Embedding Service...\n")

    test_sentences = [
        "Humayun studies at SVNIT Surat",
        "Where does Humayun go to college?",   # Similar meaning
        "The weather in Surat is hot",          # Different topic
    ]

    print("Generating embeddings...")
    embeddings = embed_batch(test_sentences)

    print(f"\n📐 Embedding dimension: {len(embeddings[0])}")
    print(f"\n🔍 Similarity Scores:")

    sim_1_2 = cosine_similarity(embeddings[0], embeddings[1])
    sim_1_3 = cosine_similarity(embeddings[0], embeddings[2])

    print(f"  '{test_sentences[0][:40]}'")
    print(f"  vs '{test_sentences[1][:40]}'")
    print(f"  Similarity: {sim_1_2:.4f} ← should be HIGH\n")

    print(f"  '{test_sentences[0][:40]}'")
    print(f"  vs '{test_sentences[2][:40]}'")
    print(f"  Similarity: {sim_1_3:.4f} ← should be LOW")

    print("\n✅ Embedding service working!")