#!/bin/bash

for week in 14 15 16; do
    mkdir ./game_predictions/week_"$week"
    python get_week_games.py --week "$week"
done
