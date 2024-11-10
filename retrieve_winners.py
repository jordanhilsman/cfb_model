import cfbd
import os
import tqdm

import pandas as pd

configuration = cfbd.Configuration()
configuration.api_key_prefix["Authorization"] = "Bearer"
configuration.api_key["Authorization"] = os.getenv("CFBD_API_KEY")
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

for file in os.listdir():
    if (".csv" in file) & ("week" in file):
        print(f"Reading {file}")
        df = pd.read_csv(file)
        tw = []
        for idx, row in tqdm.tqdm(df.iterrows(), total=len(df), desc="Getting winners.."):
            games = api_instance.get_team_game_stats(year=2024, week=2, team=row["home_team"])
            print(f"Getting winner for {row['home_team']}")
            if len(games) > 0:
                game = games[0]
                for team in game.teams:
                    if team.home_away == "home":
                        home_points = team.points
                    else:
                        away_points = team.points
                if home_points > away_points:
                    tw.append(row["home_team"])
                else:
                    tw.append(row["away_team"])
            else:
                tw.append("MANUALLY REVIEW")
        df["TRUE_WINNER"] = tw
        df.to_csv(file, index=False)
