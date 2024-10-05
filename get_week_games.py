import cfbd
import os
import subprocess

configuration = cfbd.Configuration()
configuration.api_key["Authorization"] = os.getenv("CFBD_API_KEY")
configuration.api_key_prefix["Authorization"] = "Bearer"
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

week_of_choice = int(input("What week games do you want to grab? "))

games = api_instance.get_games(year=2024, week=week_of_choice, division='fbs')

for game in games:
    away_team = game.away_team
    home_team = game.home_team
    print(f"Getting {home_team} vs {away_team}")
    subprocess.run(["python", "querying.py",
                    "--home_team", home_team,
                    "--away_team", away_team,
                    "--year", "2024", "--save"])

