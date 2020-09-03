#!/bin/bash
sleep 20
cd /home/pi/checkpointPlus_final
git fetch
git reset --hard origin/master
python  /home/pi/checkpointPlus_final/checkpointRoutine.py >/tmp/checkpoint.log 2>/tmp/checkpoint.err
