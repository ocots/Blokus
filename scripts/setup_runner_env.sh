#!/bin/bash
# ============================================================
# Blokus RL Training Environment Setup Script
# Run this ONCE on the Occidata runner to create a persistent venv
# ============================================================

set -euo pipefail

# Configuration
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
REPO_DIR="/projects/ctb/blokus-runner/_work/Blokus/Blokus/blokus-engine"

echo "🔧 Blokus RL Environment Setup"
echo "=============================="
echo "Venv location: $VENV_DIR"
echo ""

# Step 1: Check Python version
echo "📌 Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "   Found: $PYTHON_VERSION"

# Step 2: Create venv directory
echo ""
echo "📌 Step 2: Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "   ⚠️  Venv already exists at $VENV_DIR"
    read -p "   Delete and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        echo "   ✅ Venv recreated"
    else
        echo "   ℹ️  Using existing venv"
    fi
else
    python3 -m venv "$VENV_DIR"
    echo "   ✅ Venv created at $VENV_DIR"
fi

# Step 3: Activate venv
echo ""
echo "📌 Step 3: Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "   ✅ Activated: $(which python)"

# Step 4: Upgrade pip
echo ""
echo "📌 Step 4: Upgrading pip..."
pip install --upgrade pip --quiet
echo "   ✅ pip $(pip --version | cut -d' ' -f2)"

# Step 5: Install PyTorch with CUDA support
echo ""
echo "📌 Step 5: Installing PyTorch with CUDA 12.1 support..."
echo "   ⏳ This may take a few minutes (downloading ~2.5 GB)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
echo "   ✅ PyTorch installed"

# Step 6: Install other dependencies
echo ""
echo "📌 Step 6: Installing additional dependencies..."
pip install matplotlib pandas gymnasium tensorboard numpy
echo "   ✅ Dependencies installed"

# Step 7: Install blokus package
echo ""
echo "📌 Step 7: Installing blokus package..."
if [ -d "$REPO_DIR" ]; then
    pip install -e "$REPO_DIR[dev]"
    echo "   ✅ blokus installed from $REPO_DIR"
else
    echo "   ⚠️  Repo not found at $REPO_DIR"
    echo "   ℹ️  You can install it later with:"
    echo "      source $VENV_DIR/bin/activate"
    echo "      pip install -e /path/to/blokus-engine[dev]"
fi

# Step 8: Verify installation
echo ""
echo "📌 Step 8: Verifying installation..."
python -c "
import torch
print(f'   PyTorch: {torch.__version__}')
print(f'   CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'   GPU: {torch.cuda.get_device_name(0)}')
else:
    print('   ℹ️  No GPU on login node (normal, training runs on compute nodes)')
"

# Done
echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo ""
echo "To use this environment in GitHub Actions:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To update dependencies in the future:"
echo "  source $VENV_DIR/bin/activate"
echo "  pip install <package>"
echo "=============================================="
