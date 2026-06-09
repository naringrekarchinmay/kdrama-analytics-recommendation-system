# utils/loader.py
from typing import Optional

import re
from pathlib import Path

import pandas as pd
from rapidfuzz import process
import streamlit as st


def _fix_encoding(text: str) -> Optional[str]:
    if not isinstance(text, str):
        return text
    return (
        text.replace("‚Äú", '"')
            .replace("‚Äù", '"')
            .replace("‚Äô", "'")
            .replace("\\s", "'")
    )


def _normalize_title(title: str) -> str:
    if not isinstance(title, str):
        return ""
    t = title.lower().strip()
    # remove leading a/an/the
    t = re.sub(r"^(a|an|the)\s+", "", t)
    # remove punctuation
    t = re.sub(r"[^\w\s]", "", t)
    # collapse spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _fuzzy_match_title(title_clean: str, choices: list[str], threshold: int = 80) -> Optional[str]:
    """Return best fuzzy match from choices, or None if below threshold."""
    if not title_clean:
        return None
    match = process.extractOne(title_clean, choices)
    if match is None:
        return None
    best_title, score, _ = match
    if score >= threshold:
        return best_title
    return None

def _apply_platform_overrides(kdrama: pd.DataFrame, override_path: Path) -> pd.DataFrame:
    """
    Apply manual platform overrides from data/platform_overrides.csv.

    The override file should have:
    title, normalized_title, platform, notes

    Only non-empty platform values are applied.
    Blank platform values are ignored.
    """
    if not override_path.exists():
        return kdrama

    overrides = pd.read_csv(override_path)

    if "platform" not in overrides.columns:
        return kdrama

    # Keep only rows where platform has actually been filled manually
    overrides = overrides[
        overrides["platform"].notna()
        & (overrides["platform"].astype(str).str.strip() != "")
    ].copy()

    if overrides.empty:
        return kdrama

    # Create clean matching key for overrides
    if "title" in overrides.columns:
        overrides["title_clean_override"] = overrides["title"].apply(_normalize_title)
    elif "normalized_title" in overrides.columns:
        overrides["title_clean_override"] = overrides["normalized_title"].apply(_normalize_title)
    else:
        return kdrama

    platform_map = dict(
        zip(
            overrides["title_clean_override"],
            overrides["platform"].astype(str).str.strip()
        )
    )

    # Create clean matching key for master dataset
    kdrama["title_clean_for_override"] = kdrama["title"].apply(_normalize_title)

    kdrama["platform"] = kdrama.apply(
        lambda row: platform_map.get(
            row["title_clean_for_override"],
            row.get("platform", "Unknown")
        ),
        axis=1
    )

    kdrama = kdrama.drop(columns=["title_clean_for_override"], errors="ignore")

    return kdrama

@st.cache_data(show_spinner=False)
def load_and_prepare_data() -> dict:
    """
    Load CSV files, clean them, fuzzy-match titles,
    and return all core DataFrames and stats in a dict.

    Dataset priority:
    1. Use kdrama_master_updated.csv if available
    2. Fallback to original kdrama_kaggle_1500.csv
    """

    # ---- paths ----
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    master_path = data_dir / "kdrama_master_updated.csv"
    kaggle_path = data_dir / "kdrama_kaggle_1500.csv"
    my_ratings_path = data_dir / "my_kdrama_ratings.csv"
    platform_override_path = data_dir / "platform_overrides.csv"

    # ---- load personal ratings ----
    my_ratings = pd.read_csv(my_ratings_path)

    # ---- load K-drama dataset ----
    if master_path.exists():
        # New upgraded master dataset
        kdrama = pd.read_csv(master_path)

        # Apply manual platform overrides before renaming platform -> network
        kdrama = _apply_platform_overrides(kdrama, platform_override_path)

        # Rename master columns into names the current app already expects
        kdrama = kdrama.rename(
            columns={
                "start_year": "year",
                "genres": "genre",
                "global_rating": "global_score",
                "platform": "network",
                "poster_url": "img_url",
            }
        )

        kdrama["source_file"] = "kdrama_master_updated.csv"

    else:
        # Fallback to original dataset
        kdrama = pd.read_csv(kaggle_path)

        kdrama = kdrama.rename(
            columns={
                "Name": "title",
                "Year": "year",
                "Genre": "genre",
                "Main Cast": "cast",
                "Sinopsis": "synopsis",
                "Score": "global_score",
                "Content Rating": "content_rating",
                "Tags": "tags",
                "Network": "network",
                "img url": "img_url",
                "Episode": "episode_raw",
            }
        )

        kdrama["source_file"] = "kdrama_kaggle_1500.csv"

    # ---- drop unnamed junk columns ----
    kdrama = kdrama.loc[:, ~kdrama.columns.str.contains("^Unnamed")]

    # ---- ensure expected columns exist ----
    expected_columns = [
        "title",
        "year",
        "genre",
        "cast",
        "synopsis",
        "global_score",
        "content_rating",
        "tags",
        "network",
        "img_url",
        "episodes",
        "votes",
        "writer",
        "director",
        "source_dataset",
    ]

    for col in expected_columns:
        if col not in kdrama.columns:
            kdrama[col] = pd.NA

    # ---- data types ----
    kdrama["year"] = pd.to_numeric(kdrama["year"], errors="coerce")
    kdrama["global_score"] = pd.to_numeric(kdrama["global_score"], errors="coerce")

    # Episodes may come as "16 Episodes" or as a number
    if "episodes" in kdrama.columns:
        kdrama["episodes"] = (
            kdrama["episodes"]
            .astype(str)
            .str.extract(r"(\d+)")[0]
            .astype("Int64")
        )

    # ---- fix encoding for text columns ----
    for col in ["title", "synopsis", "genre", "tags", "cast", "network"]:
        if col in kdrama.columns:
            kdrama[col] = kdrama[col].apply(_fix_encoding)

    # ---- normalize titles ----
    kdrama["title_clean"] = kdrama["title"].apply(_normalize_title)
    my_ratings["title_clean"] = my_ratings["title"].apply(_normalize_title)

    # ---- fuzzy match my titles to dataset titles ----
    kaggle_titles_clean = kdrama["title_clean"].dropna().tolist()

    my_ratings["title_clean_matched"] = my_ratings["title_clean"].apply(
        lambda x: _fuzzy_match_title(x, kaggle_titles_clean, threshold=80)
    )

    # ---- merge personal ratings with drama dataset ----
    merged = my_ratings.merge(
        kdrama,
        left_on="title_clean_matched",
        right_on="title_clean",
        how="left",
        suffixes=("_me", "_kaggle"),
    )

    matched_df = merged[merged["global_score"].notna()].copy()
    unmatched_df = merged[merged["global_score"].isna()].copy()

    # ---- genre stats ----
    genre_df = matched_df[["title_me", "rating", "global_score", "genre"]].copy()

    genre_df["genre_list"] = (
        genre_df["genre"]
        .fillna("")
        .str.split(",")
        .apply(lambda lst: [g.strip() for g in lst if g.strip() != ""])
    )

    genre_exploded = genre_df.explode("genre_list")

    genre_stats = (
        genre_exploded.groupby("genre_list")
        .agg(
            my_avg_rating=("rating", "mean"),
            global_avg_score=("global_score", "mean"),
            count=("title_me", "count"),
        )
        .sort_values(["count", "my_avg_rating"], ascending=[False, False])
    )

    # ---- actor stats ----
    actor_df = matched_df[["title_me", "rating", "global_score", "cast"]].copy()

    actor_df["actor_list"] = (
        actor_df["cast"]
        .fillna("")
        .str.split(",")
        .apply(lambda lst: [a.strip() for a in lst if a.strip() != ""])
    )

    actor_exploded = actor_df.explode("actor_list")

    actor_stats = (
        actor_exploded.groupby("actor_list")
        .agg(
            my_avg_rating=("rating", "mean"),
            global_avg_score=("global_score", "mean"),
            count=("title_me", "count"),
        )
        .sort_values(["count", "my_avg_rating"], ascending=[False, False])
    )

    return {
        "kdrama": kdrama,
        "my_ratings": my_ratings,
        "merged": merged,
        "matched_df": matched_df,
        "unmatched_df": unmatched_df,
        "genre_stats": genre_stats,
        "actor_stats": actor_stats,
        "genre_exploded": genre_exploded,
        "actor_exploded": actor_exploded,
    }