# utils/recommender.py

from typing import Tuple, List, Optional

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

    candidates["why_recommended"] = candidates.apply(
        lambda r: " • ".join(
            explain_recommendation(
                r,
                user_top_genres=favorite_genres,
                user_top_actors=favorite_actors
            )
        ),
        axis=1
    )

    return candidates, favorite_genres, favorite_actors

def get_available_genres(candidates: pd.DataFrame) -> list[str]:
    """
    Return a clean sorted list of all available genres
    from the recommendation candidate table.
    """
    candidates = _ensure_lists(candidates.copy())

    all_genres = (
        candidates["genre_list"]
        .explode()
        .dropna()
        .astype(str)
        .str.strip()
    )

    all_genres = all_genres[all_genres != ""]

    return sorted(all_genres.unique().tolist())


def get_filtered_recommendations(
    candidates: pd.DataFrame,
    selected_genres: Optional[List[str]] = None,
    n_recommendations: int = 10,
    min_global_score: Optional[float] = None,
) -> pd.DataFrame:
    """
    Filter and rank recommendation candidates.

    Parameters:
    - candidates: full recommendation candidate table from build_recommendation_table()
    - selected_genres: genre/mood filters selected by the user
    - n_recommendations: number of recommendations to return
    - min_global_score: optional minimum global rating filter

    Returns:
    - filtered and ranked recommendation DataFrame
    """
    filtered = candidates.copy()
    filtered = _ensure_lists(filtered)

    # Filter by selected genres/mood
    if selected_genres:
        selected_genre_set = {
            str(genre).strip().lower()
            for genre in selected_genres
            if str(genre).strip() != ""
        }

        filtered = filtered[
            filtered["genre_list"].apply(
                lambda genre_list: bool(
                    {
                        str(genre).strip().lower()
                        for genre in genre_list
                    }
                    & selected_genre_set
                )
            )
        ].copy()

    # Optional minimum global rating filter
    if min_global_score is not None:
        filtered = filtered[
            pd.to_numeric(filtered["global_score"], errors="coerce") >= min_global_score
        ].copy()

    # Sort by recommendation score first, then global score
    filtered = filtered.sort_values(
        by=["reco_score", "global_score"],
        ascending=[False, False]
    )

    return filtered.head(n_recommendations)

def _split_list_field(val) -> list[str]:
    """
    Convert fields like "Action, Drama" or list-like strings into a clean list.
    Works for genre, tags, cast strings, etc.
    """
    if val is None:
        return []
    if isinstance(val, float):  # NaN
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    s = str(val).strip()
    if not s:
        return []
    # Most of your dataset uses commas to separate
    return [x.strip() for x in s.split(",") if x.strip()]


def _top_n_as_set(items: list[str], n: int = 5) -> set[str]:
    """Return top N items as a set (already clean strings)."""
    return set(items[:n])


def explain_recommendation(
    show_row,
    user_top_genres: list[str],
    user_top_actors: list[str],
    *,
    max_reasons: int = 3,
    min_global_score: float = 8.5
) -> list[str]:
    reasons: list[str] = []

    show_genres = show_row.get("genre_list", []) or []
    show_actors = show_row.get("actor_list", []) or []

    # Genre alignment
    matched_genres = [g for g in show_genres if g in set(user_top_genres)]
    if matched_genres:
        reasons.append(f"Matches your favorite genres: {', '.join(matched_genres[:2])}")

    # Actor affinity
    matched_actors = [a for a in show_actors if a in set(user_top_actors)]
    if matched_actors:
        reasons.append(f"Features actors you rate highly: {', '.join(matched_actors[:2])}")

    # Global score check
    try:
        gs = float(show_row.get("global_score", 0))
        if gs >= min_global_score:
            reasons.append(f"Strong global rating ({gs:.1f})")
    except Exception:
        pass

    # Fallback if none
    if not reasons:
        reasons.append("Recommended based on overall similarity to your taste profile")

    return reasons[:max_reasons]
