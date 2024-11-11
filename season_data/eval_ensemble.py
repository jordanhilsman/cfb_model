import os
import json
import pickle
import itertools

import pandas as pd


cols = [
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

models = os.listdir("../models")
models = [m for m in models if ".pkl" in m]
week_files = os.listdir()
week_files = [f for f in week_files if ".csv" in f]

ensemble_models = ["svm", "lr", "lda"]

all_models = ['gradientboost', 'knn', 'lda', 'lr',
              'nusvm', 'rf', 'svm']

permutations_of_3 = [list(comb) for comb in itertools.combinations(all_models, 3)]
indexed_perms = {index: comb for index, comb in enumerate(permutations_of_3)}

with open('all_permutations.json', 'w') as f:
    json.dump(indexed_perms, f, indent=4)

for file in week_files:
    if "Modeling" in file:
        saver = file[23:30]
        saver = saver.replace(".", "")
        saver = saver.replace(" ", "_")
    else:
        saver = file.split(".csv")[0]
    model_perf = {}
    print(f"Getting ensemble for {file}")
    df = pd.read_csv(file)
    df = df.dropna(subset="rushingTDs")
    df_sub = df[cols]
    tot = len(df)
    for model in models:
        counter = 0
        print(f"Getting predictions for {model}")
        with open(f"../models/{model}", "rb") as f:
            clf = pickle.load(f)
        name = model.split("_")[0]
        X = df_sub
        result = clf.predict(X)
        df[f"{name}_pred"] = result
        df[f"{name}_ht_win"] = clf.predict_proba(X)[:][:, 1]
        df[f"{name}_ht_lose"] = clf.predict_proba(X)[:][:, 0]
        for _, row in df.iterrows():
            if row[f"{name}_ht_win"] > row[f"{name}_ht_lose"]:
                checker = row["home_team"]
            else:
                checker = row["away_team"]
            if checker == row["TRUE_WINNER"]:
                counter += 1
        model_perf[name] = (counter / len(df)) * 100
    for idx, perm in indexed_perms.items():
        print(f"Getting predictions for ensemble {idx}")
        ensemble_prediction = []
        ensemble_counter = 0
        for _, row in df.iterrows():
            home_win_prob = 0
            for em in perm:
                home_win_prob += row[f"{em}_ht_win"]
            if home_win_prob > 1.5:
                ep = row["home_team"]
            else:
                ep = row["away_team"]
            ensemble_prediction.append(ep)
            if ep == row["TRUE_WINNER"]:
                ensemble_counter += 1
        model_perf[f"ensemble_{idx}"] = (ensemble_counter / len(df)) * 100
#        df[f"ensemble_prediction_{idx}"] = ensemble_prediction

        with open(f"performance_{saver}.txt", "w") as f:
            json.dump(model_perf, f, indent=4)

    df.to_csv(file, index=False)

dicts = os.listdir()
perf_dicts = []
for d in dicts:
    if ".txt" in d:
        with open(d, "r") as f:
            perf = json.load(f)
        perf_dicts.append(perf)

sum_dict = {key: 0 for key in perf_dicts[0]}

for dct in perf_dicts:
    for key, value in dct.items():
        sum_dict[key] += value

average_dict = {key: value / len(perf_dicts) for key, value in sum_dict.items()}
average_dict = dict(sorted(average_dict.items(), key=lambda item: item[1]))

print(average_dict)
with open("average_perf.txt", "w") as f:
    json.dump(average_dict, f, indent=4)
