#!/bin/bash

./run-all.sh "collins" "gpu0-$$" "python" "--gpu=0" "0"
./run-all.sh "collins" "gpu1-$$" "python" "--gpu=1" "0"
./run-all.sh "collins" "gpu2-$$" "python" "--gpu=2" "0"
./run-all.sh "collins" "gpu3-$$" "python" "--gpu=3" "0"
