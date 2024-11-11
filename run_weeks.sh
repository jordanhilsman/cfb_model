#!/bin/bash

for week in 12; do
    python get_week_games.py --week "$week"
done
