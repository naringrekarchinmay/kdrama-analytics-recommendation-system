# app.py

import streamlit as st

from utils.loader import load_and_prepare_data
from utils.helpers import basic_rating_stats


def main():
    st.set_page_config(
        page_title="K-Drama Analytics & Recommender",
        page_icon="🎭",
        layout="wide",
    )

    st.title("🎭 K-Drama Analytics & Recommender")
    st.write(
        "A personal K-drama analytics and recommendation dashboard combining "
        "my own watch history with a refreshed master dataset of 1,958 unique "
        "Korean dramas for taste profiling, analytics, and recommendations."
    )

    data = load_and_prepare_data()
    stats = basic_rating_stats(data["merged"], data["matched_df"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total dramas rated", stats["num_rated"])
    col2.metric("Matched with Master Dataset", stats["num_matched"])
    col3.metric("Avg my rating (matched)", f"{stats['my_mean_matched']:.2f}")
    col4.metric("Avg global rating", f"{stats['global_mean']:.2f}")

    st.markdown("---")
    st.subheader("How to use this app")
    st.markdown(
        """
        - 📊 **Analytics** page shows your rating distribution, my-vs-global comparison, favorite genres & actors.  
        - 🎯 **Recommendations** page suggests new dramas you haven't watched yet, ranked by how well they match your taste.  
        - This is **Iteration A**: a pure analytics & rules-based app. Later iterations will add Gen-AI explanations.
        """
    )


if __name__ == "__main__":
    main()
