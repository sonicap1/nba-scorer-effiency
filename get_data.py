from nba_api.stats.endpoints import leaguedashplayerstats

import pandas as pd

stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season="2025-26",
    season_type_all_star="Regular Season"
)

df = stats.get_data_frames()[0]

print(df.head())
print(df.columns.tolist())

df.to_csv("data/nba_player_stats_2025_26.csv", index=False)