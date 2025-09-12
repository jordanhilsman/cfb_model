import cfbd
import os
import pandas as pd
import argparse
import pickle

from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert

from transform_data import process_stats, retrieve_game_stats

WKS_PER_YEAR: int = 16

configuration = cfbd.Configuration(access_token=os.environ["CFBD_API_KEY"])

api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

omit_tags = ["possessionTime"]

engine = create_engine("postgresql+psycopg2://@localhost:5432/cfb_data")

metadata = MetaData()
team_stats = Table("team_stats", metadata, autoload_with=engine)

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
    parser.add_argument("--start_time", default=None)
    return parser.parse_args()


args = parse_args()

home_team = args.home_team
away_team = args.away_team
yr = args.year
weeks_to_query = args.week

if args.start_time:
    start_time = args.start_time

save_name = f"{home_team}___{away_team}___{yr}.csv"
home_team = home_team.replace("_", " ")
away_team = away_team.replace("_", " ")

teams = [home_team, away_team]

home_dict = {}
away_dict = {}

if args.allow_rematch:
    team_set = set([away_team, home_team])

for team in teams:
    for wk in range(0, weeks_to_query):
        team_game_stats = retrieve_game_stats(yr, wk, team, team_stats, weeks_to_query)
        if team_game_stats:
            if team == home_team:
                for k in team_game_stats.keys():
                    if k not in home_dict.keys():
                        home_dict[k] = [team_game_stats[k]]
                    else:
                        home_dict[k].append(team_game_stats[k])
            if team == away_team:
                for k in team_game_stats.keys():
                    if k not in away_dict.keys():
                        away_dict[k] = [team_game_stats[k]]
                    else:
                        away_dict[k].append(team_game_stats[k])

#home_means = {k: sum(v) / len(v) for k, v in home_dict.items() if v}
#away_means = {k: sum(v) / len(v) for k, v in away_dict.items() if v}

df_home = pd.DataFrame({k.lower():pd.Series(v) for k, v in home_dict.items()})
df_away = pd.DataFrame({k.lower():pd.Series(v) for k, v in away_dict.items()})

df_home = df_home.drop_duplicates(subset=['firstdowns',  'thirddowneff',  'fourthdowneff',
                                          'totalyards'])
df_away = df_away.drop_duplicates(subset=['firstdowns',  'thirddowneff',  'fourthdowneff',
                                          'totalyards'])

df_home.drop(columns=['year', 'team', 'week'], inplace=True)
df_away.drop(columns=['year', 'team', 'week'], inplace=True)

df_home = df_home.mean()
df_away = df_away.mean()

df_home = df_home.to_frame().T
df_away = df_away.to_frame().T

df_away.columns = [f"{col}_away" for col in df_away.columns]

df = pd.concat([df_home.reset_index(drop=True), df_away.reset_index(drop=True)], axis=1)

df['start_time'] = start_time

# ensemble_models = ["gradientboost", "lda", "lr"]

# ensemble_models = ['lr']

# home_team_win = 0
# home_team_lose = 0

# for em in ensemble_models:
#    with open(f"./models/{em}_model.pkl", "rb") as f:
#        lr = pickle.load(f)
#    for feature in FEATURES_ORDER:
#        if feature not in df.columns:
#            df[feature] = 0
#    df = df[FEATURES_ORDER]
#    probs = lr.predict_proba(df)
#    home_team_win += probs[0][1]
#    home_team_lose += probs[0][0]

# home_team_win = home_team_win / 3
# home_team_lose = home_team_lose / 3
# home_team_lose = home_team_lose * 100
# home_team_win = home_team_win * 100
df["home_team"] = home_team
df["away_team"] = away_team
if args.save:
    df.to_csv(f"./game_predictions/week_{weeks_to_query}/{save_name}", index=False)


