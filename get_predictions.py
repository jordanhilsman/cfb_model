import argparse
import glob
import pandas as pd

import pickle


FEATURES_ORDER = [
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
    "totalYards_rank",
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
    "totalYards_rank_away",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", type=str, help="which folder you're using")
    return parser.parse_args()


args = parse_args()
print(f"Getting predictions for {args.week}")

week = f"./game_predictions/week_{args.week}"

files = glob.glob(f"{week}/*.csv")

with open("./models/rf_model.pkl", "rb") as f:
    model = pickle.load(f)

df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

feature_conversion_dict = {feature.lower():feature for feature in model.feature_names_in_}

df = df.rename(columns={k:v for k,v in feature_conversion_dict.items()})


all_yards = pd.concat([df["totalYards"], df["totalYards_away"]])
ranks = all_yards.rank(method="dense", ascending=False).astype(int)
df["totalYards_rank"] = ranks.iloc[: len(df)].values
df["totalYards_rank_away"] = ranks.iloc[len(df) :].values



df.fillna(0, inplace=True)


probs = model.predict_proba(df[FEATURES_ORDER])

df["home_team_win"] = probs[:, 1]
df["home_team_lose"] = probs[:, 0]

df.to_csv(f"./game_predictions/2025/week_{args.week}.csv", index=False)
