#!/bin/bash

cd /home/pi/checkpointPlus_final
git fetch
git reset --hard origin/master
python  /home/pi/checkpointPlus_final/checkpointRoutine.py