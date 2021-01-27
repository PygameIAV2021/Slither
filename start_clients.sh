#!/bin/bash

#for debugging
echo "
-----------------------
-----------------------
THIS IS A DEBUG SCRIPT!
-----------------------
-----------------------


"

for i in {1..10}
do
  echo "start client $i"
  python3 start_multiplayer.py &
  sleep 0.5
done