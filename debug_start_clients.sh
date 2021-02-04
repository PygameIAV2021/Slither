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
  echo "start client $i and connect to server $1:$2"
  python3 start_multiplayer.py $1 $2 &> /dev/null &
  sleep 0.5
done