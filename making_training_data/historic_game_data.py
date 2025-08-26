import cfbd
import os

import pandas as pd

from tqdm import tqdm

from transform_data import get_team_stats, KEYS

configuration = cfbd.Configuration(access_token=os.environ["CFBD_API_KEY"])

api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

pbar = tqdm(total=len(range(2013, 2025)) * len(range(1, 17)), desc="Processing CFB Games")
for yr in range(2013, 2025):
    stats_dict_yr = {}
    for key in KEYS:
        stats_dict_yr[key] = []
    stats_dict_yr["week"] = []
    stats_dict_yr["gameID"] = []
    ids_processed = []
    for wk in range(1, 17):
        games = api_instance.get_game_team_stats(year=yr, week=wk)
        for game in games:
            if game.id in ids_processed:
                continue
            else:
                ids_processed.append(game.id)
                get_team_stats(game.teams, stats_dict_yr)
                stats_dict_yr["week"].append(wk)
                stats_dict_yr["week"].append(wk)
                stats_dict_yr["gameID"].append(game.id)
                stats_dict_yr["gameID"].append(game.id)
        pbar.update(1)
    df = pd.DataFrame.from_dict(stats_dict_yr)
    df.to_csv(f"cfb_game_data_{yr}.csv", index=False)
