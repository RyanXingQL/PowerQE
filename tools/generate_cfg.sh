#!/bin/bash

qp_values=(27 32 42 47)
qf_values=(10 20 30 40 50)
datasets=("div2k")
for dataset in "${datasets[@]}"; do
    input_file_base="configs/_base_/${dataset}.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "bpg/qp37:jpeg/qf${value}"
    done

    input_file_base="configs/_base_/${dataset}_lmdb.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}_lmdb.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qp${value}.py" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}_lmdb.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qf${value}.py" "bpg/qp37:jpeg/qf${value}"
    done

    input_file_base="configs/_base_/${dataset}_normalize.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}_normalize.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qp${value}.py" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}_normalize.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qf${value}.py" "bpg/qp37:jpeg/qf${value}"
    done

    input_file_base="configs/_base_/${dataset}_lmdb_normalize.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}_lmdb_normalize.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}_normalize.py:${dataset}_qp${value}_normalize.py" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}_lmdb_normalize.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}_normalize.py:${dataset}_qf${value}_normalize.py" "bpg/qp37:jpeg/qf${value}"
    done
done

datasets=("mfqev2" "vimeo90k_septuplet" "vimeo90k_triplet")
for dataset in "${datasets[@]}"; do
    input_file_base="configs/_base_/${dataset}.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/hm/${dataset}_qp${value}.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "qp37:qp${value}"
    done
done

methods=("basicvsr_plus_plus" "edvr" "mfqev2" "provqe" "stdf")
datasets=("mfqev2" "vimeo90k_septuplet" "vimeo90k_triplet")
for method in "${methods[@]}"; do
    for dataset in "${datasets[@]}"; do
        input_file_base="configs/${method}/${dataset}.py"
        for value in "${qp_values[@]}"; do
            output_file="configs/${method}/hm/${dataset}_qp${value}.py"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}.py:hm/${dataset}_qp${value}.py" "_${dataset}:_${dataset}_qp${value}"
        done
    done
done
