#!/bin/bash
# ============================================================
# SLURM Environment Test Script
# Run this on Occidata to validate the environment before running the workflow
# ============================================================

set -e

echo "=========================================="
echo "SLURM Environment Test"
echo "=========================================="
echo ""

# Configuration
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
WORKDIR="/projects/ctb/blokus-runner/_work/Blokus/Blokus/blokus-engine"

echo "Step 1: Testing profile sourcing..."
set +u  # Disable unbound variable check
source /etc/profile 2>/dev/null || echo "  ⚠️  /etc/profile failed"
[ -f /etc/profile.d/modules.sh ] && source /etc/profile.d/modules.sh 2>/dev/null || echo "  ⚠️  modules.sh not found"
[ -f /etc/profile.d/lmod.sh ] && source /etc/profile.d/lmod.sh 2>/dev/null || echo "  ⚠️  lmod.sh not found"
set -u  # Re-enable
echo "✅ Profile sourced"
echo ""

echo "Step 2: Testing module command..."
if command -v module &> /dev/null; then
    echo "✅ module command available"
    module avail 2>&1 | grep -i cuda || echo "  ⚠️  No CUDA modules found"
else
    echo "❌ module command NOT available"
    exit 1
fi
echo ""

echo "Step 3: Loading CUDA module..."
if module load cuda/12.2 2>&1; then
    echo "✅ CUDA module loaded"
    echo "  CUDA_HOME: ${CUDA_HOME:-not set}"
    echo "  PATH includes cuda: $(echo $PATH | grep -o cuda || echo 'NO')"
else
    echo "❌ Failed to load CUDA module"
    exit 1
fi
echo ""

echo "Step 4: Testing Python venv..."
if [ -d "$VENV_DIR" ]; then
    echo "✅ Venv exists at $VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "  Python: $(which python)"
    echo "  Version: $(python --version)"
else
    echo "❌ Venv not found at $VENV_DIR"
    exit 1
fi
echo ""

echo "Step 5: Testing PyTorch + CUDA..."
python -c "
import torch
print(f'  PyTorch version: {torch.__version__}')
print(f'  CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  CUDA version: {torch.version.cuda}')
    print(f'  GPU count: {torch.cuda.device_count()}')
else:
    print('  ⚠️  CUDA not available to PyTorch')
" || echo "❌ PyTorch import failed"
echo ""

echo "Step 6: Testing workspace..."
if [ -d "$WORKDIR" ]; then
    echo "✅ Workspace exists: $WORKDIR"
    cd "$WORKDIR"
    echo "  Current directory: $(pwd)"
else
    echo "⚠️  Workspace not found: $WORKDIR"
    echo "  This is normal if no workflow has run yet"
fi
echo ""

echo "Step 7: Testing script existence..."
if [ -f "scripts/train.py" ]; then
    echo "✅ scripts/train.py exists"
else
    echo "❌ scripts/train.py NOT found"
    echo "  Files in current directory:"
    ls -la
fi
echo ""

echo "Step 8: Testing blokus package import..."
python -c "
try:
    import blokus
    print('✅ blokus package imports successfully')
    from blokus.blokus_env import BlokusEnv
    print('✅ BlokusEnv imports successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
" || echo "❌ Package import failed"
echo ""

echo "Step 9: Testing full training command (dry run)..."
python scripts/train.py --help 2>&1 | head -n 5 || echo "❌ train.py --help failed"
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "If all steps show ✅, the SLURM environment should work."
echo "If any step shows ❌, that needs to be fixed before running the workflow."
echo ""
echo "To test on a GPU node via SLURM:"
echo "  srun --partition=GPUNodes --gres=gpu:1080ti:1 --pty bash"
echo "  Then run this script again on the compute node."
