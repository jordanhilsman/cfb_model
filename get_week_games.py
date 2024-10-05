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
for file in tqdm(os.listdir('./game_predictions/')):
    df = pd.read_csv(f"./game_predictions/{file}")
    home_team = file.split('___')[0]
    lines = api_instance.get_lines(year=2024, week=6, team=home_team)
    hml = lines[0].lines[0].home_moneyline
    aml = lines[0].lines[0].away_moneyline
    df['home_ml'] = hml
    df['away_ml'] = aml
    df.to_csv(f"./game_predictions/{file}", index=False)
