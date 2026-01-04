#!/bin/bash
#SBATCH --job-name=test-singularity
#SBATCH --output=test-singularity-%j.out
#SBATCH --error=test-singularity-%j.err
#SBATCH --partition=GPUNodes
#SBATCH --gres=gpu:1080ti:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:10:00

echo "=========================================="
echo "Singularity PyTorch Test on GPU Node"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo ""

echo "Step 1: Testing PyTorch in Singularity container..."
singularity exec /apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif python -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('CUDA version:', torch.version.cuda)
    print('GPU count:', torch.cuda.device_count())
    print('GPU name:', torch.cuda.get_device_name(0))
"

echo ""
echo "Step 2: Testing venv activation inside container..."
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
if [ -d "$VENV_DIR" ]; then
    singularity exec /apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif bash -c "
        source $VENV_DIR/bin/activate
        python --version
        python -c 'import torch; print(\"PyTorch from venv:\", torch.__version__)'
    "
else
    echo "Venv not found at $VENV_DIR"
fi

echo ""
echo "Step 3: Listing available containers..."
ls -lh /apps/containerCollections/CUDA12/*.sif

echo ""
echo "=========================================="
echo "Test completed"
echo "=========================================="
