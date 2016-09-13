#!/bin/bash

if [ $# -ne 5 ]
  then
    echo "usage: run-all.sh SYSTEM_NAME RUN_NAME EXEC SCRIPT_ARGS"
    exit
fi

SYSTEM_NAME=$1
RUN_NAME=$2
EXEC=$3
SCRIPT_ARGS=$4
DATE=$(date +%Y/%m/%d)
CPU=$(awk -F: '/model name/ {print $2;exit}' /proc/cpuinfo)

echo "Run parameters:"
echo "SYSTEM_NAME=${SYSTEM_NAME}"
echo "RUN_NAME=${RUN_NAME}"
echo "EXEC=${EXEC}"
echo "SCRIPT_ARGS=${SCRIPT_ARGS}"
echo "DATE=${DATE}"
echo "CPU=${CPU}"

root_directory=$(pwd)

: ${BENCHMARKS:="lj-liquid triblock-copolymer quasicrystal microsphere depletion hexagon"}

for benchmark in ${BENCHMARKS}
do
    workspace=$(./create_workspace.py ${benchmark} "${CPU}" ${SYSTEM_NAME} ${DATE} ${RUN_NAME} ${INDEX})

    if [ $? -ne 0 ]; then
        echo "Error creating workspace directory"
        exit
    fi

    cd ${benchmark}
    ${EXEC} ${root_directory}/${benchmark}/bmark.py ${SCRIPT_ARGS} --user=${workspace}
    cd ${root_directory}
done
