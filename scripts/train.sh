#!/usr/bin/env bash

GPUS=$1
CONFIG=$2
PORT=${PORT:-4321}

# usage
if [ $# -lt 2 ] ;then
    echo "usage:"
    echo "./scripts/train.sh [number of gpu] [path to option file]"
    exit
fi

# check if GPUS is 1 for single-GPU, otherwise run multi-GPU
if [ "$GPUS" -eq 1 ]; then
    # single GPU version
    PYTHONPATH="$(dirname $0)/..:${PYTHONPATH}" \
    python powerqe/train.py -opt $CONFIG ${@:3}
else
    # multi-GPU version
    PYTHONPATH="$(dirname $0)/..:${PYTHONPATH}" \
    python -m torch.distributed.launch --nproc_per_node=$GPUS --master_port=$PORT \
    powerqe/train.py -opt $CONFIG --launcher pytorch ${@:3}
fi