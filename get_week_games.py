import cfbd
import os
import subprocess
import pandas as pd

from tqdm import tqdm

configuration = cfbd.Configuration()
configuration.api_key["Authorization"] = os.getenv("CFBD_API_KEY")
configuration.api_key_prefix["Authorization"] = "Bearer"
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

week_of_choice = int(input("What week games do you want to grab? "))

games = api_instance.get_games(year=2024, week=week_of_choice, division='fbs')
betting_api = cfbd.BettingApi(cfbd.ApiClient(configuration))

for game in tqdm(games, total=len(games)):
    away_team = game.away_team
    home_team = game.home_team
    print(f"Getting {home_team} vs {away_team}")
    subprocess.run(["python", "querying.py",
                    "--home_team", home_team,
                    "--away_team", away_team,
                    "--year", "2024", "--save"])

print("Getting moneyline information for games...")
df_j = pd.DataFrame()
for file in tqdm(os.listdir('./game_predictions/')):
    df = pd.read_csv(f"./game_predictions/{file}")
    home_team, away_team, _ = file.split('___')[0]
    lines = betting_api.get_lines(year=2024, week=week_of_choice, team=home_team)
    if len(lines[0].lines) != 0:
        hml = lines[0].lines[0].home_moneyline
        aml = lines[0].lines[0].away_moneyline
    else:
        hml = 0
        aml = 0
    df['home_ml'] = hml
    df['away_ml'] = aml
    df['home_team'] = home_team
    df['away_team'] = away_team
    df_j = pd.concat([df_j, df])
    df.to_csv(f"./game_predictions/{file}", index=False)

df_j.to_csv(f"week_{week_of_choice}.csv", index=False)
