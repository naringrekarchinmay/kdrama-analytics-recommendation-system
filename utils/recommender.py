# utils/recommender.py

from typing import Tuple, List

import pandas as pd
import streamlit as st

from .loader import load_and_prepare_data


def _get_favorite_genres_and_actors(
    genre_stats: pd.DataFrame,
    actor_stats: pd.DataFrame,
    min_genre_count: int = 3,
    min_actor_count: int = 2,
    min_avg_rating: float = 9.0,
) -> Tuple[List[str], List[str]]:
    fav_genres = genre_stats[
        (genre_stats["count"] >= min_genre_count)
        & (genre_stats["my_avg_rating"] >= min_avg_rating)
    ]
    fav_actors = actor_stats[
        (actor_stats["count"] >= min_actor_count)
        & (actor_stats["my_avg_rating"] >= min_avg_rating)
    ]

    return fav_genres.index.tolist(), fav_actors.index.tolist()


def _ensure_lists(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure genre_list and actor_list columns exist on kdrama df."""
    if "genre_list" not in df.columns:
        df["genre_list"] = (
            df["genre"]
            .fillna("")
            .str.split(",")
            .apply(lambda lst: [g.strip() for g in lst if g.strip() != ""])
        )
    if "actor_list" not in df.columns:
        df["actor_list"] = (
            df["cast"]
            .fillna("")
            .str.split(",")
            .apply(lambda lst: [a.strip() for a in lst if a.strip() != ""])
        )
    return df


def _count_overlap(values, fav_set) -> int:
    return sum(1 for v in values if v in fav_set)


@st.cache_data(show_spinner=False)
def build_recommendation_table() -> tuple[pd.DataFrame, list[str], list[str]]:
    """
    Return:
      - candidates DataFrame with reco_score
      - favorite_genre_list
      - favorite_actor_list
    """
    data = load_and_prepare_data()
    kdrama = data["kdrama"].copy()
    my_ratings = data["my_ratings"].copy()
    genre_stats = data["genre_stats"]
    actor_stats = data["actor_stats"]

    # get favorite genres & actors
    favorite_genres, favorite_actors = _get_favorite_genres_and_actors(
        genre_stats, actor_stats
    )

    # build candidate pool = shows I haven't rated yet
    watched_titles_clean = (
        my_ratings["title_clean_matched"].dropna().unique()
    )
    kdrama = _ensure_lists(kdrama)

    candidates = kdrama[~kdrama["title_clean"].isin(watched_titles_clean)].copy()

    fav_genre_set = set(favorite_genres)
    fav_actor_set = set(favorite_actors)

    candidates["genre_overlap"] = candidates["genre_list"].apply(
        lambda lst: _count_overlap(lst, fav_genre_set)
    )
    candidates["actor_overlap"] = candidates["actor_list"].apply(
        lambda lst: _count_overlap(lst, fav_actor_set)
    )

    # normalize global score
    candidates["global_score_norm"] = candidates["global_score"] / 10.0

    candidates["reco_score"] = (
        candidates["global_score_norm"] * 0.5
        + candidates["genre_overlap"] * 0.3
        + candidates["actor_overlap"] * 0.2
    )

    return candidates, favorite_genres, favorite_actors
