import cfbd
import os

configuration = cfbd.Configuration()
configuration.api_key["Authorization"] = os.getenv("CFBD_API_KEY")
configuration.api_key_prefix["Authorization"] = "Bearer"
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

fields_of_interest = ["fourthDownEff", "thirdDownEff", "totalPenaltiesYards", "completionAttempts"]

# 1 if team1 == home, 0 if team2 == home
# 1 if team1 wins, 0 if team2 wins

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

stat_keys = keys[4:]
stats_dictionary = {}
for key in keys:
    stats_dictionary[key] = []


def get_team_stats(teams, stats_dictionary):
    team1 = teams[0].to_dict()
    team2 = teams[1].to_dict()
    for team in teams:
        team_cur = team.to_dict()
        if team_cur == team1:
            if team1["points"] > team2["points"]:
                stats_dictionary["winner"].append(1)
            else:
                stats_dictionary["winner"].append(0)
            if team1["home_away"] == "home":
                stats_dictionary["home"].append(1)
            else:
                stats_dictionary["home"].append(0)
            stats_dictionary["points"].append(team1["points"])
            stats_dictionary["school"].append(team1["school"])
        if team_cur == team2:
            if team2["points"] > team1["points"]:
                stats_dictionary["winner"].append(1)
            else:
                stats_dictionary["winner"].append(0)
            if team2["home_away"] == "home":
                stats_dictionary["home"].append(1)
            else:
                stats_dictionary["home"].append(0)
            stats_dictionary["points"].append(team2["points"])
            stats_dictionary["school"].append(team2["school"])
        cur_team = team_cur["stats"]
        for stat_update in stat_keys:
            update_val = 0
            for stat in cur_team:
                if stat["category"] == stat_update:
                    update_val = stat["stat"]
                    if stat["category"] not in fields_of_interest:
                        update_val = float(stat["stat"])
                    else:
                        if len(stat["stat"].split("-")) != 2:
                            val1, val2 = 0, 0
                        else:
                            val1, val2 = stat["stat"].split("-")
                        if (int(val1) == 0) | (int(val2) == 0):
                            update_val = 0
                        else:
                            update_val = int(val1) / int(val2)
            stats_dictionary[stat_update].append(update_val)


# pbar = tqdm(total=len(range(2023,2024))*len(range(1,17)), desc = "Processing CFB Games")
# for yr in range(2023, 2024):
#    stats_dict_yr = {}
#    for key in keys:
#        stats_dict_yr[key] = []
#    ids_processed = []
#    for wk in range(1, 17):
#        games = api_instance.get_team_game_stats(year=yr, week=wk)
#        for game in games:
#            if game.id in ids_processed:
#                continue
#            else:
#                ids_processed.append(game.id)
#                get_team_stats(game.teams, stats_dict_yr)
#        pbar.update(1)
#    df = pd.DataFrame.from_dict(stats_dict_yr)
#    df.to_csv(f'cfb_game_data_{yr}.csv', index=False)

# df = pd.DataFrame.from_dict(stats_dictionary)

# df.to_csv('cfb_stats_2013_2023.csv', index=False)

# print(stats_dictionary)
