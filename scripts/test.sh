#!/usr/bin/env bash

GPUS=$1
CONFIG=$2
PORT=${PORT:-4321}

# usage
if [ $# -lt 2 ] ;then
    echo "usage:"
    echo "./scripts/test.sh [number of gpu] [path to option file]"
    exit
fi

# check if GPUS is 1 for single-GPU, otherwise run multi-GPU
if [ "$GPUS" -eq 1 ]; then
    # if only one GPU, run the simple version
    PYTHONPATH="$(dirname $0)/..:${PYTHONPATH}" \
    python powerqe/test.py -opt $CONFIG ${@:3}
else
    # if multiple GPUs, run the distributed version
    PYTHONPATH="$(dirname $0)/..:${PYTHONPATH}" \
    python -m torch.distributed.launch --nproc_per_node=$GPUS --master_port=$PORT \
    powerqe/test.py -opt $CONFIG --launcher pytorch ${@:3}
fi
