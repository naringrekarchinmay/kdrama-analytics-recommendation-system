# pages/2_Analytics.py

import streamlit as st

from utils.loader import load_and_prepare_data
from utils.visuals import rating_histogram, rating_vs_global_scatter


def run():
    st.title("📊 My K-Drama Analytics")

    data = load_and_prepare_data()
    merged = data["merged"]
    matched_df = data["matched_df"]
    genre_stats = data["genre_stats"]
    actor_stats = data["actor_stats"]

    st.subheader("Rating Distribution")
    st.altair_chart(rating_histogram(merged), use_container_width=True)

    st.subheader("My Rating vs Global Score")
    st.altair_chart(rating_vs_global_scatter(matched_df), use_container_width=True)

    st.markdown("### Favorite Genres (min 3 shows)")
    fav_genres = genre_stats[genre_stats["count"] >= 3].copy()
    st.dataframe(
        fav_genres[["my_avg_rating", "global_avg_score", "count"]]
        .sort_values(["my_avg_rating"], ascending=False)
        .round(2)
    )

    st.markdown("### Favorite Actors (min 2 shows)")
    fav_actors = actor_stats[actor_stats["count"] >= 2].copy()
    st.dataframe(
        fav_actors[["my_avg_rating", "global_avg_score", "count"]]
        .sort_values(["count", "my_avg_rating"], ascending=[False, False])
        .round(2)
    )


if __name__ == "__main__":
    run()
