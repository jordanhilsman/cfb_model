import cfbd
import os

import numpy as np

from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert

configuration = cfbd.Configuration(access_token=os.environ["CFBD_API_KEY"])
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

metadata = MetaData()

engine = create_engine("postgresql+psycopg2://@localhost:5432/cfb_data")

team_stats = Table("team_stats", metadata, autoload_with=engine)

fields_of_interest = ["fourthDownEff", "thirdDownEff", "totalPenaltiesYards", "completionAttempts"]

omit_tags = ['possessionTime']


KEYS: list = [
    "winner",
    "home",
    "points",
    "team",
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

stat_keys = KEYS[4:]
stats_dictionary = {}
for key in KEYS:
    stats_dictionary[key] = []


def get_team_stats(teams, stats_dictionary=stats_dictionary):
    team1 = teams[0].to_dict()
    team2 = teams[1].to_dict()
    for team in teams:
        team_cur = team.to_dict()
        if team_cur == team1:
            if team1["points"] > team2["points"]:
                stats_dictionary["winner"].append(1)
            else:
                stats_dictionary["winner"].append(0)
            if team1["homeAway"] == "home":
                stats_dictionary["home"].append(1)
            else:
                stats_dictionary["home"].append(0)
            stats_dictionary["points"].append(team1["points"])
            stats_dictionary["team"].append(team1["team"])
        if team_cur == team2:
            if team2["points"] > team1["points"]:
                stats_dictionary["winner"].append(1)
            else:
                stats_dictionary["winner"].append(0)
            if team2["homeAway"] == "home":
                stats_dictionary["home"].append(1)
            else:
                stats_dictionary["home"].append(0)
            stats_dictionary["points"].append(team2["points"])
            stats_dictionary["team"].append(team2["team"])
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
    return stats_dictionary


def process_stats(stat_dict):
    if ("-" in stat_dict) & (stat_dict[0] != "-"):
        if len(stat_dict.split("-")) != 2:
            val1, val2 = 0, 0
        else:
            val1, val2 = stat_dict.split("-")
        if (int(val1) == 0) | (int(val2) == 0):
            return 0
        else:
            return int(val1) / int(val2)
    else:
        try:
            return float(stat_dict)
        except ValueError:
            return 0

def retrieve_game_stats(year, week, team, team_stats, week_to_query):
    with engine.begin() as conn:
        stmt = (
                team_stats.select()
                .where(team_stats.c.year == year)
                .where(team_stats.c.week == week)
                .where(team_stats.c.team == team)
                )
        result = conn.execute(stmt).mappings().first()
        if result:
            result = {k:np.nan if v is None else v for k, v in result.items()}
            return result
        if week_to_query != 1:
            games = api_instance.get_game_team_stats(year=year, week=week, team=team)
        else:
            games = api_instance.get_game_team_stats(year=year-1, week=12, team=team)
            if not games:
                games = api_instance.get_game_team_stats(year=year-1, week=11, team=team)
        if len(games) >= 1:
            game = games[0]
            team_stats_only = [tm for tm in game.teams if tm.team == team]
            result = {stat["category"]:process_stats(stat["stat"]) for stat in team_stats_only[0].to_dict()['stats'] if stat['category'] not in omit_tags}
            result['team'] = team
            result['week'] = week
            result['year'] = year
            stmt = insert(team_stats).values({k.lower():v for k,v in result.items()})
            stmt = stmt.on_conflict_do_nothing(index_elements=["year", "week", "team"])
            conn.execute(stmt)
            return result
