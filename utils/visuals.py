# utils/visuals.py

import altair as alt
import pandas as pd


def rating_histogram(merged: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(merged)
        .mark_bar()
        .encode(
            x=alt.X("rating:Q", bin=alt.Bin(maxbins=10), title="My Rating"),
            y=alt.Y("count():Q", title="Count"),
        )
        .properties(height=300)
    )


def rating_vs_global_scatter(matched_df: pd.DataFrame) -> alt.Chart:
    chart = (
        alt.Chart(matched_df)
        .mark_circle(size=70, opacity=0.7)
        .encode(
            x=alt.X("global_score:Q", title="Global Score"),
            y=alt.Y("rating:Q", title="My Rating"),
            tooltip=["title_me", "rating", "global_score"],
        )
        .properties(height=350)
    )

    line = (
        alt.Chart(pd.DataFrame({"x": [7, 10], "y": [7, 10]}))
        .mark_line(strokeDash=[5, 5], color="gray")
        .encode(x="x:Q", y="y:Q")
    )

    return chart + line
