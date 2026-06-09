# pages/3_Recommendations.py

import streamlit as st
import pandas as pd

from utils.recommender import (
    build_recommendation_table,
    get_available_genres,
    get_filtered_recommendations,
)


def run():
    st.title("🎯 Recommendations")

    candidates, favorite_genres, favorite_actors = build_recommendation_table()

    st.markdown("#### My favorite genres (used in scoring)")
    st.write(", ".join(favorite_genres) if favorite_genres else "None detected yet")

    st.markdown("#### My favorite actors (used in scoring)")
    st.write(", ".join(favorite_actors) if favorite_actors else "None detected yet")

    st.markdown("---")

    st.subheader("🎛️ Recommendation Filters")

    # Build available genre list from recommendation candidates
    available_genres = get_available_genres(candidates)

    selected_genres = st.multiselect(
        "What genre are you in the mood for?",
        options=available_genres,
        default=[],
        help="Select one or more genres. Example: Romance, Comedy, Thriller."
    )

    top_n = st.slider(
        "How many recommendations to show?",
        min_value=5,
        max_value=30,
        value=10,
        step=5
    )

    min_global_score = st.slider(
        "Minimum global score",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
        help="Use this if you only want higher-rated recommendations."
    )

    # Apply filters and return ranked recommendations
    top_recos = get_filtered_recommendations(
        candidates=candidates,
        selected_genres=selected_genres,
        n_recommendations=top_n,
        min_global_score=min_global_score if min_global_score > 0 else None,
    )

    st.markdown("---")

    if selected_genres:
        st.subheader(f"📺 Suggested dramas for: {', '.join(selected_genres)}")
    else:
        st.subheader("📺 Suggested dramas you haven't watched yet")

    if top_recos.empty:
        st.warning(
            "No recommendations found for the selected filters. "
            "Try selecting fewer genres or lowering the minimum global score."
        )
        return

    # Show each recommendation as a card
    for _, row in top_recos.iterrows():
        with st.container(border=True):
            col_img, col_info = st.columns([1, 2])

            with col_img:
                if isinstance(row.get("img_url"), str) and row["img_url"].strip():
                    st.image(row["img_url"], use_container_width=True)
                else:
                    st.write("No image")

            with col_info:
                title = row.get("title", "Unknown title")
                year = int(row["year"]) if not pd.isna(row["year"]) else "?"
                st.markdown(f"### {title} ({year})")

                global_score = row.get("global_score", None)
                reco_score = row.get("reco_score", None)

                if not pd.isna(global_score) and not pd.isna(reco_score):
                    st.markdown(
                        f"**Global score:** {global_score:.2f} &nbsp;&nbsp; "
                        f"**Reco score:** {reco_score:.3f}"
                    )

                st.markdown(
                    f"**Genre overlap:** {int(row['genre_overlap'])} &nbsp;&nbsp; "
                    f"**Actor overlap:** {int(row['actor_overlap'])}"
                )

                if isinstance(row.get("genre"), str) and row["genre"].strip():
                    st.markdown(f"**Genres:** {row['genre']}")

                if isinstance(row.get("network"), str) and row["network"].strip():
                    st.markdown(f"**Platform / Network:** {row['network']}")

                if isinstance(row.get("cast"), str) and row["cast"].strip():
                    st.markdown(f"**Cast:** {row['cast']}")

                why = row.get("why_recommended", "")
                if isinstance(why, str) and why.strip():
                    st.markdown(f"**Why recommended:** {why}")

    # Optional: show the raw table below
    with st.expander("Show raw recommendation table"):
        display_columns = [
            "title",
            "year",
            "global_score",
            "genre",
            "network",
            "cast",
            "genre_overlap",
            "actor_overlap",
            "reco_score",
            "why_recommended",
        ]

        existing_columns = [
            col for col in display_columns
            if col in top_recos.columns
        ]

        st.dataframe(
            top_recos[existing_columns].round(
                {"global_score": 2, "reco_score": 3}
            ),
            use_container_width=True,
        )


if __name__ == "__main__":
    run()