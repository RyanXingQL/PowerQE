#!/bin/bash

qp_values=(27 32 42 47)
qf_values=(10 20 30 40 50)
datasets=("div2k")
for dataset in "${datasets[@]}"; do
    input_file_base="configs/_base_/${dataset}.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}.py"
        # python tools/generate_cfg.py "configs/_base_/div2k.py" "configs/_base_/bpg/div2k_qp27.py" "qp37:qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}.py"
        # python tools/generate_cfg.py "configs/_base_/div2k.py" "configs/_base_/jpeg/div2k_qf10.py" "bpg/qp37:jpeg/qf10"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "bpg/qp37:jpeg/qf${value}"
    done

    input_file_base="configs/_base_/${dataset}_lmdb.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}_lmdb.py"
        # python tools/generate_cfg.py "configs/_base_/div2k_lmdb.py" "configs/_base_/bpg/div2k_qp27_lmdb.py" "div2k.py:div2k_qp27.py" "qp37:qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qp${value}.py" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}_lmdb.py"
        # python tools/generate_cfg.py "configs/_base_/div2k_lmdb.py" "configs/_base_/jpeg/div2k_qf10_lmdb.py" "div2k.py:div2k_qf10.py" "bpg/qp37:jpeg/qf10"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qf${value}.py" "bpg/qp37:jpeg/qf${value}"
    done

    input_file_base="configs/_base_/${dataset}_normalize.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}_normalize.py"
        # python tools/generate_cfg.py "configs/_base_/div2k_normalize.py" "configs/_base_/bpg/div2k_qp27_normalize.py" "div2k.py:div2k_qp27.py" "qp37:qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qp${value}.py" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}_normalize.py"
        # python tools/generate_cfg.py "configs/_base_/div2k_normalize.py" "configs/_base_/jpeg/div2k_qf10_normalize.py" "div2k.py:div2k_qf10.py" "bpg/qp37:jpeg/qf10"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qf${value}.py" "bpg/qp37:jpeg/qf${value}"
    done

    input_file_base="configs/_base_/${dataset}_lmdb_normalize.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/bpg/${dataset}_qp${value}_lmdb_normalize.py"
        # python tools/generate_cfg.py "configs/_base_/div2k_lmdb_normalize.py" "configs/_base_/bpg/div2k_qp27_lmdb_normalize.py" "div2k_normalize.py:div2k_qp27_normalize.py" "qp37:qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}_normalize.py:${dataset}_qp${value}_normalize.py" "qp37:qp${value}"
    done
    for value in "${qf_values[@]}"; do
        output_file="configs/_base_/jpeg/${dataset}_qf${value}_lmdb_normalize.py"
        # python tools/generate_cfg.py "configs/_base_/div2k_lmdb_normalize.py" "configs/_base_/jpeg/div2k_qf10_lmdb_normalize.py" "div2k_normalize.py:div2k_qf10_normalize.py" "bpg/qp37:jpeg/qf10"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}_normalize.py:${dataset}_qf${value}_normalize.py" "bpg/qp37:jpeg/qf${value}"
    done
done

methods=("arcnn" "cbdnet" "dcad" "dncnn" "mprnet" "rdn")
datasets=("div2k")
for method in "${methods[@]}"; do
    for dataset in "${datasets[@]}"; do
        input_file_base="configs/${method}/${dataset}_lmdb.py"
        for value in "${qp_values[@]}"; do
            output_file="configs/${method}/bpg/${dataset}_qp${value}_lmdb.py"
            # python tools/generate_cfg.py "configs/arcnn/div2k_lmdb.py" "configs/arcnn/bpg/div2k_qp27_lmdb.py" "../_base_:../../_base_" "div2k_lmdb.py:bpg/div2k_qp27_lmdb.py" "_div2k:_div2k_qp27"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_lmdb.py:bpg/${dataset}_qp${value}_lmdb.py" "_${dataset}:_${dataset}_qp${value}"
        done

        input_file_base="configs/${method}/${dataset}_lmdb.py"
        for value in "${qf_values[@]}"; do
            output_file="configs/${method}/jpeg/${dataset}_qf${value}_lmdb.py"
            # python tools/generate_cfg.py "configs/arcnn/div2k_lmdb.py" "configs/arcnn/jpeg/div2k_qf10_lmdb.py" "../_base_:../../_base_" "div2k_lmdb.py:bpg/div2k_qf10_lmdb.py" "_div2k:_div2k_qf10"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_lmdb.py:jpeg/${dataset}_qf${value}_lmdb.py" "_${dataset}:_${dataset}_qf${value}"
        done
    done
done

methods=("esrgan")
datasets=("div2k")
for method in "${methods[@]}"; do
    for dataset in "${datasets[@]}"; do
        input_file_base="configs/${method}/${dataset}_stage1_lmdb.py"

        for value in "${qp_values[@]}"; do
            output_file="configs/${method}/bpg/${dataset}_qp${value}_stage1_lmdb.py"
            # python tools/generate_cfg.py "configs/esrgan/div2k_stage1_lmdb.py" "configs/esrgan/bpg/div2k_qp27_stage1_lmdb.py" "../_base_:../../_base_" "div2k_lmdb_normalize.py:bpg/div2k_qp27_lmdb_normalize.py" "_div2k:_div2k_qp27"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_lmdb_normalize.py:bpg/${dataset}_qp${value}_lmdb_normalize.py" "_${dataset}:_${dataset}_qp${value}"
        done

        for value in "${qf_values[@]}"; do
            output_file="configs/${method}/jpeg/${dataset}_qf${value}_stage1_lmdb.py"
            # python tools/generate_cfg.py "configs/esrgan/div2k_stage1_lmdb.py" "configs/esrgan/jpeg/div2k_qf10_stage1_lmdb.py" "../_base_:../../_base_" "div2k_lmdb_normalize.py:jpeg/div2k_qf10_lmdb_normalize.py" "_div2k:_div2k_qf10"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_lmdb_normalize.py:jpeg/${dataset}_qf${value}_lmdb_normalize.py" "_${dataset}:_${dataset}_qf${value}"
        done

        input_file_base="configs/${method}/${dataset}_stage2_lmdb.py"

        for value in "${qp_values[@]}"; do
            output_file="configs/${method}/bpg/${dataset}_qp${value}_stage2_lmdb.py"
            # python tools/generate_cfg.py "configs/esrgan/div2k_stage2_lmdb.py" "configs/esrgan/bpg/div2k_qp27_stage2_lmdb.py" "_stage1:_qp27_stage1" "_stage2:_qp27_stage2"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "_stage1:_qp${value}_stage1" "_stage2:_qp${value}_stage2"
        done

        for value in "${qf_values[@]}"; do
            output_file="configs/${method}/jpeg/${dataset}_qf${value}_stage2_lmdb.py"
            # python tools/generate_cfg.py "configs/esrgan/div2k_stage2_lmdb.py" "configs/esrgan/jpeg/div2k_qf10_stage2_lmdb.py" "_stage1:_qf10_stage1" "_stage2:_qf10_stage2"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "_stage1:_qf${value}_stage1" "_stage2:_qf${value}_stage2"
        done
    done
done

methods=("rbqe")
datasets=("div2k")
for method in "${methods[@]}"; do
    for dataset in "${datasets[@]}"; do
        input_file_base="configs/${method}/non_blind_${dataset}_lmdb.py"

        for value in "${qp_values[@]}"; do
            output_file="configs/${method}/bpg/non_blind_${dataset}_qp${value}_lmdb.py"
            # python tools/generate_cfg.py "configs/rbqe/non_blind_div2k_lmdb.py" "configs/rbqe/bpg/non_blind_div2k_qp27_lmdb.py" "../_base_:../../_base_" "div2k_lmdb.py:bpg/div2k_qp27_lmdb.py" "_div2k:_div2k_qp27"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_lmdb.py:bpg/${dataset}_qp${value}_lmdb.py" "_${dataset}:_${dataset}_qp${value}"
        done

        for value in "${qf_values[@]}"; do
            output_file="configs/${method}/jpeg/non_blind_${dataset}_qf${value}_lmdb.py"
            # python tools/generate_cfg.py "configs/rbqe/non_blind_div2k_lmdb.py" "configs/rbqe/jpeg/non_blind_div2k_qf10_lmdb.py" "../_base_:../../_base_" "div2k_lmdb.py:bpg/div2k_qf10_lmdb.py" "_div2k:_div2k_qf10"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_lmdb.py:jpeg/${dataset}_qf${value}_lmdb.py" "_${dataset}:_${dataset}_qf${value}"
        done
    done
done

datasets=("mfqev2" "vimeo90k_septuplet" "vimeo90k_triplet")
for dataset in "${datasets[@]}"; do
    input_file_base="configs/_base_/${dataset}.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/hm/${dataset}_qp${value}.py"
        # python tools/generate_cfg.py "configs/_base_/mfqev2.py" "configs/_base_/hm/mfqev2_qp27.py" "qp37:qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "qp37:qp${value}"
    done

    input_file_base="configs/_base_/${dataset}_normalize.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/_base_/hm/${dataset}_qp${value}_normalize.py"
        # python tools/generate_cfg.py "configs/_base_/mfqev2_normalize.py" "configs/_base_/hm/mfqev2_qp27_normalize.py" "mfqev2.py:mfqev2_qp27.py"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "${dataset}.py:${dataset}_qp${value}.py"
    done
done

methods=("basicvsr_plus_plus" "mfqev2" "stdf")
datasets=("mfqev2" "vimeo90k_septuplet" "vimeo90k_triplet")
for method in "${methods[@]}"; do
    for dataset in "${datasets[@]}"; do
        input_file_base="configs/${method}/${dataset}.py"
        for value in "${qp_values[@]}"; do
            output_file="configs/${method}/hm/${dataset}_qp${value}.py"
            # python tools/generate_cfg.py "configs/basicvsr_plus_plus/mfqev2.py" "configs/basicvsr_plus_plus/hm/mfqev2_qp27.py" "../_base_:../../_base_" "mfqev2.py:hm/mfqev2_qp27.py" "_mfqev2:_mfqev2_qp27"
            python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}.py:hm/${dataset}_qp${value}.py" "_${dataset}:_${dataset}_qp${value}"
        done
    done
done

datasets=("mfqev2" "vimeo90k_septuplet" "vimeo90k_triplet")
for dataset in "${datasets[@]}"; do
    input_file_base="configs/edvr/${dataset}.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/edvr/hm/${dataset}_qp${value}.py"
        # python tools/generate_cfg.py "configs/edvr/mfqev2.py" "configs/edvr/hm/mfqev2_qp27.py" "../_base_:../../_base_" "mfqev2_normalize.py:hm/mfqev2_qp27_normalize.py" "_mfqev2:_mfqev2_qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "../_base_:../../_base_" "${dataset}_normalize.py:hm/${dataset}_qp${value}_normalize.py" "_${dataset}:_${dataset}_qp${value}"
    done

    input_file_base="configs/provqe/${dataset}.py"
    for value in "${qp_values[@]}"; do
        output_file="configs/provqe/hm/${dataset}_qp${value}.py"
        # python tools/generate_cfg.py "configs/provqe/mfqev2.py" "configs/provqe/hm/mfqev2_qp27.py" "../basicvsr_plus_plus/mfqev2.py:../../basicvsr_plus_plus/hm/mfqev2_qp27.py" "_mfqev2:_mfqev2_qp27"
        python tools/generate_cfg.py "$input_file_base" "$output_file" "../basicvsr_plus_plus/${dataset}.py:../../basicvsr_plus_plus/hm/${dataset}_qp${value}.py" "_${dataset}:_${dataset}_qp${value}"
    done
done
