import cfbd
import os
import subprocess
import pandas as pd
import argparse

from datetime import datetime
from tqdm import tqdm

configuration = cfbd.Configuration(access_token=os.environ["CFBD_API_KEY"])
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
betting_api = cfbd.BettingApi(cfbd.ApiClient(configuration))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", type=int, required=True)
    return parser.parse_args()


args = parse_args()
week_of_choice = args.week

games_all = api_instance.get_games(year=2025, week=week_of_choice)
games = []
for game in games_all:
    if (game.home_classification is not None) & (game.away_classification is not None):
        if (game.home_classification.value == 'fbs') | (game.away_classification.value == 'fbs'):
            games.append(game)

for game in tqdm(games, total=len(games)):
    away_team = game.away_team
    home_team = game.home_team
    start_time = game.start_date
    print(f"Getting {home_team} vs {away_team}")
    subprocess.run(
        [
            "python",
            "querying.py",
            "--home_team",
            home_team,
            "--away_team",
            away_team,
            "--year",
            "2025",
            "--save",
            "--week",
            f"{week_of_choice}",
            "--start_time",
            f"{start_time}"
        ]
    )

print("Getting moneyline information for games...")
#df_j = pd.DataFrame()
#for file in tqdm(os.listdir(f"./game_predictions/week_{week_of_choice}")):
#    if "___" in file:
#        df = pd.read_csv(f"./game_predictions/week_{week_of_choice}/{file}")
#        home_team, away_team, _ = file.split("___")
#        lines = betting_api.get_lines(year=2025, week=week_of_choice, team=home_team)
#        print(home_team)
#        if (len(lines) == 0) | (lines[0].lines == []):
#            hml = 0
#            aml = 0
#            dt = 0
#        else:
#            hml = lines[0].lines[0].home_moneyline
#            aml = lines[0].lines[0].away_moneyline
#            date_time_str = lines[0].start_date
#            dt = datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
#
#        df["home_ml"] = hml
#        df["away_ml"] = aml
#        df["home_team"] = home_team
#        df["away_team"] = away_team
##        df["start_date_time"] = dt
##        df_j = pd.concat([df_j, df])
#        df.to_csv(f"./game_predictions/week_{week_of_choice}/{file}", index=False)

#df_j.to_csv(f"week_{week_of_choice}.csv", index=False)
