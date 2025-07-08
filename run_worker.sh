#!/usr/bin/env bash
# File: run_worker.sh
# Usage: ./run_worker.sh

set -euo pipefail          # fail fast on errors or unset vars
IFS=$'\n\t'                # safer word-splitting

# 1. Threading hygiene for OpenBLAS
export OPENBLAS_NUM_THREADS=1
export OPENBLAS_MAIN_FREE=1

# 2. HPC module system (requires Bash, not /bin/sh)
source /usr/local/ngseq/etc/lmod_profile
export MODULEPATH=/usr/local/ngseq/etc/modules

module load Dev/uv \
            Tools/bcl2fastq \
            Aligner/CellRanger \
            Aligner/CellRangerARC \
            Tools/Bases2Fastq
# source ./venv25/bin/activate  # activate the virtual environment

# 4. Launch your worker
source ./.venv/bin/activate  # activate the virtual environment
python3 scripts/worker.py --queues="$(hostname)"
