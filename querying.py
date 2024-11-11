import cfbd
import os
import pickle
import numpy as np
import pandas as pd
import argparse
from transform_data import get_team_stats

WKS_PER_YEAR: int = 16

keys = [
    "winner",
    "home",
    "points",
    "school",
    "rushingTDs",
    "puntReturnYards",
    "puntReturnTDs",
    "puntReturns",
    "passingTDs",
    "kickReturnYards",
    "kickReturnTDs",
    "kickReturns",
    "kickingPoints",
    "interceptionYards",
    "interceptionTDs",
    "passesIntercepted",
    "fumblesRecovered",
    "totalFumbles",
    "tacklesForLoss",
    "defensiveTDs",
    "tackles",
    "sacks",
    "qbHurries",
    "passesDeflected",
    "interceptions",
    "fumblesLost",
    "turnovers",
    "totalPenaltiesYards",
    "yardsPerRushAttempt",
    "rushingAttempts",
    "rushingYards",
    "yardsPerPass",
    "completionAttempts",
    "netPassingYards",
    "totalYards",
    "fourthDownEff",
    "thirdDownEff",
    "firstDowns",
]

col_order = [
    "rushingTDs_away",
    "puntReturnYards_away",
    "puntReturnTDs_away",
    "puntReturns_away",
    "passingTDs_away",
    "kickReturnYards_away",
    "kickReturnTDs_away",
    "kickReturns_away",
    "kickingPoints_away",
    "interceptionYards_away",
    "interceptionTDs_away",
    "passesIntercepted_away",
    "fumblesRecovered_away",
    "totalFumbles_away",
    "tacklesForLoss_away",
    "defensiveTDs_away",
    "tackles_away",
    "sacks_away",
    "qbHurries_away",
    "passesDeflected_away",
    "interceptions_away",
    "fumblesLost_away",
    "turnovers_away",
    "totalPenaltiesYards_away",
    "yardsPerRushAttempt_away",
    "rushingAttempts_away",
    "rushingYards_away",
    "yardsPerPass_away",
    "completionAttempts_away",
    "netPassingYards_away",
    "totalYards_away",
    "fourthDownEff_away",
    "thirdDownEff_away",
    "firstDowns_away",
    "rushingTDs",
    "puntReturnYards",
    "puntReturnTDs",
    "puntReturns",
    "passingTDs",
    "kickReturnYards",
    "kickReturnTDs",
    "kickReturns",
    "kickingPoints",
    "interceptionYards",
    "interceptionTDs",
    "passesIntercepted",
    "fumblesRecovered",
    "totalFumbles",
    "tacklesForLoss",
    "defensiveTDs",
    "tackles",
    "sacks",
    "qbHurries",
    "passesDeflected",
    "interceptions",
    "fumblesLost",
    "turnovers",
    "totalPenaltiesYards",
    "yardsPerRushAttempt",
    "rushingAttempts",
    "rushingYards",
    "yardsPerPass",
    "completionAttempts",
    "netPassingYards",
    "totalYards",
    "fourthDownEff",
    "thirdDownEff",
    "firstDowns",
]

stat_keys = keys[4:]

configuration = cfbd.Configuration()
configuration.api_key_prefix["Authorization"] = "Bearer"
configuration.api_key["Authorization"] = os.getenv("CFBD_API_KEY")

api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        "Arguments for matchup configurations, home team, away team, year of matchup"
    )
    parser.add_argument("--home_team", type=str, help="Home team for matchup")
    parser.add_argument("--away_team", type=str, help="Away team for matchup")
    parser.add_argument("--year", type=int, help="Year of matchup")
    parser.add_argument(
        "--allow_rematch",
        action="store_true",
        help="Consider previous matchup of the teams, defaults false",
    )
    parser.add_argument("--save", action="store_true", help="To save .csv of results or not")
    parser.add_argument("--week", type=int, default=16)
    return parser.parse_args()


args = parse_args()

home_team = args.home_team
away_team = args.away_team
yr = args.year
weeks_to_query = args.week

save_name = f"{home_team}___{away_team}___{yr}.csv"
home_team = home_team.replace("_", " ")
away_team = away_team.replace("_", " ")

teams = [home_team, away_team]

dict_home = {}
dict_away = {}

for key in keys:
    dict_home[key] = []
    dict_away[key] = []

if args.allow_rematch:
    team_set = set([away_team, home_team])

for team in teams:
    for wk in range(1, weeks_to_query):
        if weeks_to_query != 1:
            games = api_instance.get_team_game_stats(year=yr, week=wk, team=team)
        else:
            games = api_instance.get_team_game_stats(year=(yr - 1), week=16, team=team)
        if len(games) >= 1:
            game_teams = games[0].teams
            if args.allow_rematch:
                team_names = set([tm["school"] for tm in game_teams])
                if team_names == team_set:
                    continue
                else:
                    if team == home_team:
                        get_team_stats(game_teams, dict_home)
                    elif team == away_team:
                        get_team_stats(game_teams, dict_away)
            else:
                if team == home_team:
                    get_team_stats(game_teams, dict_home)
                elif team == away_team:
                    get_team_stats(game_teams, dict_away)
        else:
            continue

df_home = pd.DataFrame.from_dict(dict_home)
df_away = pd.DataFrame.from_dict(dict_away)

n_row_home = len(df_home)
n_row_away = len(df_away)

df_home["ID"] = np.repeat(range(1, n_row_home // 2 + 1), 2)
df_away["ID"] = np.repeat(range(1, n_row_away // 2 + 1), 2)

df_home = df_home[df_home["school"] == home_team]
df_away = df_away[df_away["school"] == away_team]

df_home.drop(columns=["school", "points", "winner", "ID", "home"], inplace=True)
df_away.drop(columns=["school", "points", "winner", "ID", "home"], inplace=True)

df_home.loc["mean"] = df_home.mean()
df_away.loc["mean"] = df_away.mean()

df_away.columns = [f"{col}_away" for col in df_away.columns]

df_home = df_home.loc["mean"].to_frame().T
df_away = df_away.loc["mean"].to_frame().T

df = pd.concat([df_home, df_away], axis=1)
df = df.reindex(columns=col_order)

ensemble_models = ["gradientboost", "lda", "lr"]

home_team_win = 0
home_team_lose = 0

for em in ensemble_models:
    with open(f"./models/{em}_model.pkl", "rb") as f:
        lr = pickle.load(f)
    probs = lr.predict_proba(df)
    home_team_win += probs[0][1]
    home_team_lose += probs[0][0]

home_team_win = home_team_win / 3
home_team_lose = home_team_lose / 3
home_team_lose = home_team_lose * 100
home_team_win = home_team_win * 100

df["home_win_proba"] = home_team_win
df["home_lose_proba"] = home_team_lose

if args.save:
    df.to_csv(f"./game_predictions/week_{weeks_to_query}/{save_name}", index=False)


print(f"The probability the Home team ({home_team}) wins is: {home_team_win:2f}%")
print(f"The probability the Away Team ({away_team}) wins is: {home_team_lose:2f}%")
