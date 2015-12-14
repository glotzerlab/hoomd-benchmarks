#!/bin/bash

./run-all.sh "collins" "gpu0-$$" "hoomd" "--gpu=0" "0"
./run-all.sh "collins" "gpu1-$$" "hoomd" "--gpu=1" "0"
./run-all.sh "collins" "gpu2-$$" "hoomd" "--gpu=2" "0"
./run-all.sh "collins" "gpu3-$$" "hoomd" "--gpu=3" "0"
