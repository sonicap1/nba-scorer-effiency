import streamlit as st
import pandas as pd
import plotly.express as px

#load NBA data
df = pd.read_csv("data/nba_player_stats_2025_26.csv")

st.title("What Makes and Efficient NBA Scorer")

st.write(
    "An interactive analysis of scoring efficiency among NBA players during the 2025-26 season."
)

st.write(df.head())

#create PPG
df["PTS_PER_GAME"] = df["PTS"] / df["GP"]

#500 mins played restriction
qualified_df = df[df["MIN"] >= 500].copy()

#calculate TS%
qualified_df["TS_PCT"] = qualified_df["PTS"] / (
    2 * (qualified_df["FGA"] + 0.44 * qualified_df["FTA"])
)

#15 PPG restriction
scorers_df = qualified_df[
    qualified_df["PTS_PER_GAME"] >= 15
].copy()

st.write("Players in analysis:", len(scorers_df))

st.header("Scoring Volume vs. Efficiency")

fig = px.scatter(
    scorers_df,
    x="PTS_PER_GAME",
    y="TS_PCT",
    hover_name="PLAYER_NAME",
    hover_data={
        "TEAM_ABBREVIATION": True,
        "PTS_PER_GAME": ":.1f",
        "TS_PCT": ":.3f"
    },
    labels={
        "PTS_PER_GAME": "Points Per Game",
        "TS_PCT": "True Shooting Percentage",
        "TEAM_ABBREVIATION": "Team"
    },
    title="Points Per Game vs. True Shooting Percentage"
)

fig.update_yaxes(tickformat=".0%")

st.plotly_chart(fig, width="stretch")

#calculate scoring metrics
scorers_df["THREE_POINT_ATTEMPT_RATE"] = (
    scorers_df["FG3A"] / scorers_df["FGA"]
)

scorers_df["FREE_THROW_RATE"] = (
    scorers_df["FTA"] / scorers_df["FGA"]
)

scorers_df["FG2_PCT"] = (
    (scorers_df["FGM"] - scorers_df["FG3M"])
    / (scorers_df["FGA"] - scorers_df["FG3A"])
)

st.header("Factors Associated with Scoring Efficiency")

correlations = {
    "2P%": scorers_df["FG2_PCT"].corr(scorers_df["TS_PCT"]),
    "3P%": scorers_df["FG3_PCT"].corr(scorers_df["TS_PCT"]),
    "FT%": scorers_df["FT_PCT"].corr(scorers_df["TS_PCT"]),
    "3PA Rate": scorers_df["THREE_POINT_ATTEMPT_RATE"].corr(scorers_df["TS_PCT"]),
    "FT Rate": scorers_df["FREE_THROW_RATE"].corr(scorers_df["TS_PCT"]),
    "PPG": scorers_df["PTS_PER_GAME"].corr(scorers_df["TS_PCT"])
}

correlation_df = pd.DataFrame(
    list(correlations.items()),
    columns=["Metric", "Correlation"]
)

st.write(correlation_df)

correlation_df = correlation_df.sort_values(
    "Correlation",
    ascending=True
)

correlation_fig = px.bar(
    correlation_df,
    x="Correlation",
    y="Metric",
    orientation="h",
    title="Correlation with True Shooting Percentage"
)

correlation_fig.add_vline(x=0)

st.plotly_chart(correlation_fig, width="stretch")

st.write(
    """
    Two-point percentage has the strongest positive association with true shooting percentage
    in this sample, followed by free-throw rate. Points per game has a weaker positive
    relationship with scoring efficiency, while three-point attempt rate has a slight
    negative relationship.
    """
)

st.header("Player Scoring Profiles")

selected_player = st.selectbox(
    "Selecr a player:",
    sorted(scorers_df["PLAYER_NAME"].unique())
)

st.write("Selected player:", selected_player)

#player scoring profiles
profile_columns = [
    "FG2_PCT",
    "FG3_PCT",
    "FT_PCT",
    "THREE_POINT_ATTEMPT_RATE",
    "FREE_THROW_RATE"
]

profile_means = scorers_df[profile_columns].mean()
profile_stds = scorers_df[profile_columns].std()

selected_profile = scorers_df[
    scorers_df["PLAYER_NAME"] == selected_player
][profile_columns].iloc[0]

selected_zscores = (
    selected_profile - profile_means
) / profile_stds

profile_df = pd.DataFrame({
    "Metric": [
        "2P%",
        "3P%",
        "FT%",
        "3PA Rate",
        "FT Rate"
    ],
    "Z-Score": selected_zscores.values
})

profile_fig = px.bar(
    profile_df,
    x="Metric",
    y="Z-Score",
    title=f"{selected_player} Scoring Profile"
)

profile_fig.add_hline(y=0)

st.plotly_chart(profile_fig, width="stretch")

#compare scoring profiles
st.header("Compare Scoring Profiles")

selected_players = st.multiselect(
    "Select players to compare:",
    sorted(scorers_df["PLAYER_NAME"].unique()),
)

if selected_players:

    comparison_rows = []

    for player in selected_players:

        player_profile = scorers_df[
            scorers_df["PLAYER_NAME"] == player
        ][profile_columns].iloc[0]

        player_zscores = (
            player_profile - profile_means
        ) / profile_stds

        for metric, zscore in zip(
            ["2P%", "3P%", "FT%", "3PA Rate", "FT Rate"],
            player_zscores.values
        ):
            comparison_rows.append({
                "PLAYER_NAME": player,
                "Metric": metric,
                "Z-Score": zscore
            })

    comparison_df = pd.DataFrame(comparison_rows)

    comparison_fig = px.bar(
        comparison_df,
        x="Metric",
        y="Z-Score",
        color="PLAYER_NAME",
        barmode="group",
        title="Player Scoring Profile Comparison"
    )

    comparison_fig.add_hline(y=0)

    st.plotly_chart(comparison_fig, width="stretch")

else:
    st.write("Select players above to compare their scoring profiles.")