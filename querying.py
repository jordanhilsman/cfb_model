import cfbd
import os
import pandas as pd
import argparse
from transform_data import process_stats

WKS_PER_YEAR: int = 16

configuration = cfbd.Configuration(access_token=os.environ["CFBD_API_KEY"])

api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

omit_tags = ["possessionTime"]


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

home_dict = {}
away_dict = {}

if args.allow_rematch:
    team_set = set([away_team, home_team])

for team in teams:
    for wk in range(0, weeks_to_query):
        if weeks_to_query != 1:
            games = api_instance.get_game_team_stats(year=2025, week=wk, team=team)
        else:
            games = api_instance.get_game_team_stats(year=2024, week=12, team=team)
            if not games:
                games = api_instance.get_game_team_stats(2024, week=11, team=team)
        if len(games) >= 1:
            game = games[0]
            if team == home_team:
                home_stats = [team for team in game.teams if team.team == home_team]
                for stat in home_stats[0].to_dict()["stats"]:
                    if (stat["category"] not in home_dict.keys()) & (
                        stat["category"] not in omit_tags
                    ):
                        home_dict[stat["category"]] = [process_stats(stat["stat"])]
                    else:
                        if stat["category"] not in omit_tags:
                            home_dict[stat["category"]].append(process_stats(stat["stat"]))
            elif team == away_team:
                away_stats = [team for team in game.teams if team.team == away_team]
                for stat in away_stats[0].to_dict()["stats"]:
                    if (stat["category"] not in away_dict.keys()) & (
                        stat["category"] not in omit_tags
                    ):
                        away_dict[stat["category"]] = [process_stats(stat["stat"])]
                    else:
                        if stat["category"] not in omit_tags:
                            away_dict[stat["category"]].append(process_stats(stat["stat"]))


home_means = {k: sum(v) / len(v) for k, v in home_dict.items() if v}
away_means = {k: sum(v) / len(v) for k, v in away_dict.items() if v}


# df_home = pd.DataFrame.from_dict(home_means)
# df_away = pd.DataFrame.from_dict(away_means)

df_home = pd.DataFrame([home_means])
df_away = pd.DataFrame([away_means])


df_away.columns = [f"{col}_away" for col in df_away.columns]

df = pd.concat([df_home.reset_index(drop=True), df_away.reset_index(drop=True)], axis=1)

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


# print(f"The probability the Home team ({home_team}) wins is: {home_team_win:2f}%")
# print(f"The probability the Away Team ({away_team}) wins is: {home_team_lose:2f}%")
