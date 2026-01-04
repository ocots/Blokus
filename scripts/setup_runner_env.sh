#!/bin/bash
# ============================================================
# Blokus RL Environment Setup Script (Singularity Version)
# Run this ONCE on the Occidata runner to create a persistent venv
# compatible with the PyTorch Singularity container.
# ============================================================

set -euo pipefail

# Configuration
# Using the tested and working container
CONTAINER="/apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif"
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
REPO_DIR="/projects/ctb/blokus-runner/_work/Blokus/Blokus/blokus-engine"

echo "🔧 Blokus RL Environment Setup (Singularity)"
echo "============================================"
echo "Container: $CONTAINER"
echo "Venv location: $VENV_DIR"
echo ""

# Step 1: Check Singularity
echo "📌 Step 1: Checking Singularity..."
if ! command -v singularity &> /dev/null; then
    echo "❌ Singularity could not be found. Check your environment modules."
    exit 1
fi
singularity --version
echo "✅ Singularity found"
echo ""

# Step 2: Create venv directory inside container
echo "📌 Step 2: Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "   ⚠️  Venv already exists at $VENV_DIR"
    read -p "   Delete and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   🗑️  Removing old venv..."
        rm -rf "$VENV_DIR"
        
        echo "   🔨 Creating new venv inside container..."
        singularity exec "$CONTAINER" virtualenv --system-site-packages "$VENV_DIR"
        echo "   ✅ Venv recreated"
    else
        echo "   ℹ️  Using existing venv"
    fi
else
    echo "   🔨 Creating new venv inside container..."
    singularity exec "$CONTAINER" virtualenv --system-site-packages "$VENV_DIR"
    echo "   ✅ Venv created at $VENV_DIR"
fi
echo ""

# Step 3: Upgrade pip and install dependencies inside container
echo "📌 Step 3: Installing dependencies..."
echo "   Dependencies: matplotlib, pandas, gymnasium, tensorboard, numpy, flit"
echo ""

singularity exec "$CONTAINER" bash -c "
    set -e
    source \"$VENV_DIR/bin/activate\"
    
    echo '   ⬆️  Upgrading pip...'
    pip install --upgrade pip --quiet
    
    echo '   📦 Installing packages...'
    pip install matplotlib pandas gymnasium tensorboard numpy flit --quiet
    
    echo '   ✅ Packages installed'
"
echo ""

# Step 4: Verify installation
echo "📌 Step 4: Verifying installation..."
singularity exec "$CONTAINER" bash -c "
    source \"$VENV_DIR/bin/activate\"
    python -c \"
import torch
import numpy
import matplotlib
import pandas
print(f'   ✅ PyTorch: {torch.__version__} (from container)')
print(f'   ✅ CUDA available: {torch.cuda.is_available()} (False is normal on login node)')
print(f'   ✅ NumPy: {numpy.__version__}')
print(f'   ✅ Matplotlib: {matplotlib.__version__}')
print(f'   ✅ Pandas: {pandas.__version__}')
    \"
"

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo "=============================================="
echo "To use this environment manually:"
echo "  singularity shell $CONTAINER"
echo "  source $VENV_DIR/bin/activate"
echo ""
