from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from pathlib import Path

import pandas as pd
import numpy as np
import hashlib

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "data" / "titles.csv"

def get_dataset_fingerprint(df):
    """Generate a fingerprint based on the dataset's contents."""
    dataset_bytes = pd.util.hash_pandas_object(
        df,
        index=True,
    ).values.tobytes()

    return hashlib.sha256(dataset_bytes).hexdigest()

def load_dataset():
    """Load and validate the Cine Heist dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    required_columns = {
        "media_type",
        "id",
        "title",
        "overview",
        "genre",
        "original_language",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Dataset is missing columns: {sorted(missing_columns)}")

    df["overview"] = df["overview"].fillna("").str.strip()
    df["genre"] = df["genre"].fillna("")

    return df

def build_recommendation_text(df):
    """Combine plot descriptions and metadata for recommendations."""

    df = df.copy()

    metadata_columns = [
        "title",
        "overview",
        "genre",
        "keywords",
        "cast",
        "director",
    ]

    for column in metadata_columns:
        if column not in df.columns:
            df[column] = ""

        df[column] = df[column].fillna("").astype(str).str.strip()

    df["recommendation_text"] = (
        "Title: " + df["title"] + ". "
        "Plot: " + df["overview"] + ". "
        "Genres: " + df["genre"] + ". "
        "Keywords: " + df["keywords"] + ". "
        "Cast: " + df["cast"] + ". "
        "Director: " + df["director"] + "."
    )

    return df


def build_embedding_model(df):
    """Load cached embeddings or generate metadata-aware embeddings."""

    model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings_path = PROJECT_ROOT / "data" / "embeddings.npy"
    fingerprint_path = PROJECT_ROOT / "data" / "embeddings.sha256"

    # Build combined text if it hasn't been created yet.
    if "recommendation_text" not in df.columns:
        df = build_recommendation_text(df)

    current_fingerprint = get_dataset_fingerprint(
        df[["recommendation_text"]]
    )

    if embeddings_path.exists() and fingerprint_path.exists():
        saved_fingerprint = fingerprint_path.read_text(
            encoding="utf-8"
        ).strip()

        if saved_fingerprint == current_fingerprint:
            embeddings = np.load(embeddings_path)

            if embeddings.shape == (len(df), 384):
                print("Loaded cached embeddings.")
                return model, embeddings

        print("Dataset changed or cache is invalid. Regenerating embeddings.")

    embeddings = model.encode(
        df["recommendation_text"].tolist(),
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    np.save(embeddings_path, embeddings)

    fingerprint_path.write_text(
        current_fingerprint,
        encoding="utf-8",
    )

    print(f"Saved embeddings to: {embeddings_path}")
    print("Saved dataset fingerprint.")

    return model, embeddings


def recommend_by_embedding(
    query,
    df,
    model,
    embeddings,
    top_n=5,
    media_type=None,
    language=None,
):
    """Recommend titles using semantic similarity and optional filters."""

    query = query.strip()

    if not query:
        return df.iloc[0:0].copy()

    # Identify titles that match the requested filters.
    mask = pd.Series(True, index=df.index)

    if media_type:
        mask &= df["media_type"].str.lower() == media_type.lower()

    if language:
        mask &= (
            df["original_language"].str.lower()
            == language.lower()
        )

    # Keep the original row positions for indexing embeddings.
    matching_positions = [
        position
        for position, matches in enumerate(mask.to_numpy())
        if matches
    ]

    if not matching_positions:
        return df.iloc[0:0].copy()

    # Convert the query into an embedding.
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    # Calculate similarity only against matching titles.
    candidate_embeddings = embeddings[matching_positions]

    scores = cosine_similarity(
        query_embedding,
        candidate_embeddings,
    ).flatten()

    # Select the highest-scoring results.
    top_n = max(1, int(top_n))
    ranked_positions = scores.argsort()[::-1][:top_n]

    result_positions = [
        matching_positions[position]
        for position in ranked_positions
    ]

    results = df.iloc[result_positions].copy()
    results["similarity_score"] = scores[ranked_positions]

    return results