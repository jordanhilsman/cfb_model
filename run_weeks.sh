#!/bin/bash

for week in 5 12; do
    python get_week_games.py --week "$week"
done
