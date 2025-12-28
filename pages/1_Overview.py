# pages/1_Overview.py

import streamlit as st

from utils.loader import load_and_prepare_data
from utils.helpers import basic_rating_stats, find_local_poster


def run():
    st.title("📖 Overview")

    data = load_and_prepare_data()
    merged = data["merged"]
    stats = basic_rating_stats(merged, data["matched_df"])

    st.write("High-level summary of my K-drama watching profile:")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total rated", stats["num_rated"])
    col2.metric("Matched in dataset", stats["num_matched"])
    col3.metric("Avg diff (Me - Global)", f"{stats['mean_diff']:.2f}")

    st.markdown("### Dataset info")
    st.write(f"Total dramas in Kaggle dataset: **{data['kdrama'].shape[0]}**")
    st.write(f"My rated dramas: **{merged.shape[0]}**")

    st.markdown(
        """
        This app is built on:
        - 🧾 My personal ratings (`my_kdrama_ratings.csv`)  
        - 📚 Kaggle dataset of 1500+ K-dramas (`kdrama_kaggle_1500.csv`)  
        - 🔍 Fuzzy title matching + genre & actor analysis  
        """
    )

    st.markdown("---")
    st.subheader("🎬 All dramas I've rated (poster wall)")

    # We’ll only show rows where we have an image URL
    posters_df = merged.copy()

    # Prefer Kaggle title if present, else my title
    posters_df["display_title"] = posters_df["title_me"].fillna(posters_df.get("title", ""))

    # Sort by my rating (highest first)
    posters_df = posters_df.sort_values("rating", ascending=False)

    # How many posters per row
    posters_per_row = 5
    rows = (len(posters_df) + posters_per_row - 1) // posters_per_row

    # How many posters per row
    posters_per_row = 5
    rows = (len(posters_df) + posters_per_row - 1) // posters_per_row

    for row_idx in range(rows):
        cols = st.columns(posters_per_row)
        for col_idx in range(posters_per_row):
            i = row_idx * posters_per_row + col_idx
            if i >= len(posters_df):
                break

            row = posters_df.iloc[i]
            with cols[col_idx]:
                img_url = row.get("img_url")
                local_poster = find_local_poster(row["display_title"])

                # 🔁 Prefer my local poster if it exists
                if local_poster is not None:
                    st.image(local_poster, use_container_width=True)
                elif isinstance(img_url, str) and img_url.strip():
                    st.image(img_url, use_container_width=True)
                else:
                    st.write("No image")

                st.caption(f"{row['display_title']}  ⭐ {row['rating']:.1f}")


if __name__ == "__main__":
    run()
