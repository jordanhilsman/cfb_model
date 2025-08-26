import pandas as pd

df = pd.read_csv("ALL_GAME_DATA_2013_2024.csv")

df = df.copy()
non_stat_cols = ["winner", "home", "points", "team", "week", "gameID", "year"]
stat_cols = [c for c in df.columns if c not in non_stat_cols]
df = df.sort_values(by=["team", "year", "week"])


def apply_rolling(group):
    # compute expanding mean shifted by 1 (prior weeks only)
    rolling_means = group[stat_cols].expanding().mean().shift(1)
    for col in stat_cols:
        rolling_means[col] = rolling_means[col].fillna(group[col])
    group[stat_cols] = rolling_means
    return group


new_df = df.groupby(["team", "year"], group_keys=False).apply(apply_rolling).reset_index(drop=True)

new_df["totalYards_rank"] = new_df.groupby(["year", "week"])["totalYards"].rank(
    method="dense", ascending=False
)
new_df.drop(columns=["year", "week", "winner"], inplace=True)

home = new_df[new_df["home"] == 1]
away = new_df[new_df["home"] == 0]

away.drop(columns=["home"], inplace=True)
home.drop(columns=["home"], inplace=True)

merged_df = pd.merge(home, away, left_on="gameID", right_on="gameID", suffixes=["", "_away"])

merged_df.loc[(merged_df["points"] < merged_df["points_away"]), "DID_HOME_WIN"] = 0
merged_df.loc[(merged_df["points"] > merged_df["points_away"]), "DID_HOME_WIN"] = 1

merged_df = merged_df.sample(frac=1, random_state=1337)
merged_df.drop(columns=["points", "points_away"], inplace=True)

merged_df.to_csv("TRAINING_DATA.csv", index=False)
