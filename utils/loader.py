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


@st.cache_data(show_spinner=False)
def load_and_prepare_data() -> dict:
    """
    Load CSV files, clean them, fuzzy-match titles and
    return all core DataFrames and stats in a dict.
    """
    # ---- paths ----
    base_dir = Path(__file__).resolve().parent.parent  # project root (Kdrama_analytics)
    data_dir = base_dir / "data"

    kaggle_path = data_dir / "kdrama_kaggle_1500.csv"
    my_ratings_path = data_dir / "my_kdrama_ratings.csv"

    # ---- load ----
    kdrama = pd.read_csv(kaggle_path)
    my_ratings = pd.read_csv(my_ratings_path)

    # ---- clean kaggle columns ----
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
    # drop unnamed junk
    kdrama = kdrama.loc[:, ~kdrama.columns.str.contains("^Unnamed")]

    # types
    kdrama["year"] = pd.to_numeric(kdrama["year"], errors="coerce")
    kdrama["global_score"] = pd.to_numeric(kdrama["global_score"], errors="coerce")

    # extract numeric episodes
    kdrama["episodes"] = (
        kdrama["episode_raw"]
        .astype(str)
        .str.extract(r"(\d+)")
        .astype("Int64")
    )

    # fix encoding
    for col in ["title", "synopsis", "genre", "tags", "cast"]:
        if col in kdrama.columns:
            kdrama[col] = kdrama[col].apply(_fix_encoding)

    # ---- normalize titles ----
    kdrama["title_clean"] = kdrama["title"].apply(_normalize_title)
    my_ratings["title_clean"] = my_ratings["title"].apply(_normalize_title)

    # ---- fuzzy match my titles to kaggle ----
    kaggle_titles_clean = kdrama["title_clean"].tolist()
    my_ratings["title_clean_matched"] = my_ratings["title_clean"].apply(
        lambda x: _fuzzy_match_title(x, kaggle_titles_clean, threshold=80)
    )

    # ---- merge ----
    merged = my_ratings.merge(
        kdrama,
        left_on="title_clean_matched",
        right_on="title_clean",
        how="left",
        suffixes=("_me", "_kaggle"),
    )

    matched_df = merged[merged["global_score"].notna()].copy()
    unmatched_df = merged[merged["global_score"].isna()].copy()

    # ---- genre & actor exploded tables for stats ----
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
