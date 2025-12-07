# utils/helpers.py

from pathlib import Path
import re
from typing import Optional
import pandas as pd


def basic_rating_stats(merged: pd.DataFrame, matched_df: pd.DataFrame) -> dict:
    """Return simple summary stats for overview cards."""
    my_all = merged["rating"].describe()
    my_matched = matched_df["rating"].describe()
    global_stats = matched_df["global_score"].describe()

    rating_diff = matched_df["rating"] - matched_df["global_score"]
    diff_stats = rating_diff.describe()

    return {
        "num_rated": int(merged.shape[0]),
        "num_matched": int(matched_df.shape[0]),
        "num_unmatched": int(merged.shape[0] - matched_df.shape[0]),
        "my_mean_all": float(my_all["mean"]),
        "my_mean_matched": float(my_matched["mean"]),
        "global_mean": float(global_stats["mean"]),
        "mean_diff": float(diff_stats["mean"]),
    }
def find_local_poster(title: str) -> Optional[str]:
    """
    Try to find a local poster image for this title in the `missing_posters` folder.
    Returns the file path as a string if found, else None.
    """
    if not isinstance(title, str) or not title.strip():
        return None

    base_dir = Path(__file__).resolve().parent.parent  # project root
    poster_dir = base_dir / "missing_posters"

    if not poster_dir.exists():
        return None

    # normalize title: lowercase, remove punctuation, collapse spaces
    def normalize(text: str) -> str:
        t = text.lower()
        t = re.sub(r"[^\w\s]", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    target = normalize(title)

    for path in poster_dir.iterdir():
        if not path.is_file():
            continue
        stem_norm = normalize(path.stem)
        if stem_norm == target:
            return str(path)

    return None
