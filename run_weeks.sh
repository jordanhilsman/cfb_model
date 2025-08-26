#!/bin/bash

for week in 1; do
        mkdir ./game_predictions/week_"$week"
        python get_week_games.py --week "$week"
        python get_predictions.py --week "$week"
    done
