#!/bin/bash

cd /home/pi/checkpointPlus_final
git fetch
git reset --hard origin/master
python  /home/pi/checkpointPlus_final/checkpointRoutinev4.py >/tmp/checkpoint.log 2>/tmp/checkpoint.err
