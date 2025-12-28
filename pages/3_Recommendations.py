# pages/3_Recommendations.py

import streamlit as st
import pandas as pd


from utils.recommender import build_recommendation_table
from utils.recommender import explain_recommendation



def run():
    st.title("🎯 Recommendations")

    candidates, favorite_genres, favorite_actors = build_recommendation_table()

    st.markdown("#### My favorite genres (used in scoring)")
    st.write(", ".join(favorite_genres) if favorite_genres else "None detected yet")

    st.markdown("#### My favorite actors (used in scoring)")
    st.write(", ".join(favorite_actors) if favorite_actors else "None detected yet")

    st.markdown("---")

    top_n = st.slider("How many recommendations to show?", 5, 30, 10, step=5)

    top_recos = (
        candidates.sort_values("reco_score", ascending=False)
        .head(top_n)
        .copy()
    )

    st.subheader("📺 Suggested dramas you haven't watched yet")

    # Show each recommendation as a 'card'
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

                st.markdown(
                    f"**Global score:** {row['global_score']:.2f} &nbsp;&nbsp; "
                    f"**Reco score:** {row['reco_score']:.3f}"
                )

                st.markdown(
                    f"**Genre overlap:** {int(row['genre_overlap'])} &nbsp;&nbsp; "
                    f"**Actor overlap:** {int(row['actor_overlap'])}"
                )

                if isinstance(row.get("genre"), str) and row["genre"].strip():
                    st.markdown(f"**Genres:** {row['genre']}")
                if isinstance(row.get("cast"), str) and row["cast"].strip():
                    st.markdown(f"**Cast:** {row['cast']}")
                # Why recommended
                why = row.get("why_recommended", "")
                if isinstance(why, str) and why.strip():
                    st.markdown(f"**Why recommended:** {why}")

    # Optional: show the raw table below
    with st.expander("Show raw recommendation table"):
        st.dataframe(
            top_recos[
                [
                    "title",
                    "year",
                    "global_score",
                    "genre",
                    "cast",
                    "genre_overlap",
                    "actor_overlap",
                    "reco_score",
                    "why_recommended",
                ]
            ].round({"global_score": 2, "reco_score": 3}),
            use_container_width=True,
        )


if __name__ == "__main__":
    import pandas as pd  # needed for pd.isna in standalone run
    run()
