#!/bin/bash
#SBATCH --job-name=sdxl_batch
#SBATCH --partition=all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=run_outputs/logs/%x-%j.out

set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WORKSPACE_ROOT="$(dirname "$REPO_ROOT")"
cd "$REPO_ROOT"
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export HF_HOME="$WORKSPACE_ROOT/ReNO/hf_cache"
export HF_HUB_CACHE="$HF_HOME/hub"
PYTHON="${SAE_DEMO_PYTHON:-/n/fs/goose/el8403/conda-envs/reno/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python environment not found: $PYTHON" >&2
  echo "Set SAE_DEMO_PYTHON in your SLURM environment to the Python executable with torch and diffusers." >&2
  exit 2
fi

if [[ $# -ne 1 ]]; then
  echo "Usage: sbatch generation/generate_batch.slurm CONFIG.json" >&2
  exit 2
fi

"$PYTHON" -u generation/generate_batch.py "$1"
