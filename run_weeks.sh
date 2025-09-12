#!/bin/bash

weeks=$1

echo "Getting games for week $weeks"

for week in $weeks; do
        mkdir ./game_predictions/week_"$week"
        python get_week_games.py --week "$week"
        python get_predictions.py --week "$week"
    done
