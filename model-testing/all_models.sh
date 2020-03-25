#!/bin/bash

set -x
source /Users/nikhil.phatak/my/nlp-project/ghostwriter/venv/bin/activate
## declare an array variable
declare -a arr=("gpt2" "ctrl" "openai-gpt" "xlnet" "transfo-xl" "xlm")

## now loop through the above array
for i in "${arr[@]}"
do
   echo "$i"
   echo "$1" | python3 examples/run_generation.py --model_type="$i" --model_name_or_path="$i" --length=100
   # or do whatever with individual element of the array
done
