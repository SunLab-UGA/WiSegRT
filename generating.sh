#!/bin/bash
iteration=$1
for ((i=0;i<$1;i++)); do
    echo "$3 tx $i"
    python generating.py $2 $3 $4 $5 $6 $7 $i
done
