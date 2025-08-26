import os

import pandas as pd

df = pd.DataFrame()

for file in os.listdir():
    if file.endswith(".csv"):
        df_year = pd.read_csv(file)
        df_year["year"] = file.split("_")[-1].split(".")[0]
        df = pd.concat([df, df_year], axis=0, ignore_index=True)

df.to_csv("ALL_GAME_DATA_2013_2024.csv", index=False)
