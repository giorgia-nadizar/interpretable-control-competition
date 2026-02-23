#!/bin/bash

# Usage: ./generate_json_problem_instance.sh <seed> <occupancy_rate> <type> <n_flights> <output_name>

seed=$1
occupancy_rate=$2
type=$3
n_flights=$4
output_name=$5

# If output name does not end with .json, append it
if [[ $output_name != *.json ]]; then
    output_name="${output_name}.json"
fi

python3 generate_instance.py -s $seed -or $occupancy_rate -t $type -f $n_flights -v -o problems/ -on $output_name -pp -pm arrivals
python3 json2PDDL.py -i problems/$output_name -o problems/

