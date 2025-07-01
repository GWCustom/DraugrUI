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

module load Dev/Python \
            Tools/bcl2fastq \
            Aligner/CellRanger \
            Aligner/CellRangerARC \
            Tools/Bases2Fastq

# 3. Conda environment (activate only after Python module so that
#    conda’s version wins; if you want the module’s Python, drop this)
eval "$(conda shell.bash hook)"   # defines the 'conda' shell function
conda activate gi_py3.11.5

# 4. Launch your worker
python3 scripts/worker.py --queues="$(hostname)"
