#!/bin/bash
set -e  # Exit on error

# Configuration
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
PROJECT_ROOT="$(pwd)/blokus-engine"
EXPERIMENTS_DIR="$PROJECT_ROOT/models/experiments"

# Default target (can be overridden by argument)
TARGET_EXP="duo_gpu_2h_run_v1_20260104_211851"
if [ "$1" ]; then
    TARGET_EXP="$1"
fi

EXPERIMENT_PATH="$EXPERIMENTS_DIR/$TARGET_EXP"
METRICS_FILE="$EXPERIMENT_PATH/metrics.csv"
PLOT_OUTPUT="$EXPERIMENT_PATH/training_plot.png"

echo "========================================================"
echo "🔧 Manual Plot Recovery Script"
echo "========================================================"
echo "Date: $(date)"
echo "Host: $(hostname)"
echo "User: $(whoami)"
echo "========================================================"

# Check Venv
if [ -d "$VENV_DIR" ]; then
    echo "✅ Persistent venv found at $VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "   Activated venv."
else
    echo "❌ Venv NOT found at $VENV_DIR"
    exit 1
fi

echo "--------------------------------------------------------"
echo "📦 Checking Dependencies..."

if python -c "import matplotlib" 2>/dev/null; then
    echo "✅ Matplotlib is already installed."
else
    echo "⚠️  Matplotlib not found. Installing dependencies..."
    if [ -d "blokus-engine" ]; then
        cd blokus-engine
        pip install -e ".[dev]"
        cd ..
        echo "✅ Dependencies updated."
    else
        echo "❌ Could not find blokus-engine directory"
        exit 1
    fi
fi

echo "--------------------------------------------------------"
echo "📈 Generating Plot..."
echo "Target Experiment: $TARGET_EXP"
echo "Metrics File: $METRICS_FILE"

if [ ! -f "$METRICS_FILE" ]; then
    echo "❌ Metrics file not found at expected path."
    echo ""
    echo "Available experiments in $EXPERIMENTS_DIR:"
    if [ -d "$EXPERIMENTS_DIR" ]; then
        ls -1 "$EXPERIMENTS_DIR"
    else
        echo "❌ Experiments directory not found at $EXPERIMENTS_DIR"
    fi
    echo ""
    echo "Usage: bash scripts/recover_plots_manual.sh [EXPERIMENT_NAME]"
    exit 1
fi

# Locate script
SCRIPT_PATH="blokus-engine/scripts/plot_metrics.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Could not find plot_metrics.py at $SCRIPT_PATH"
    exit 1
fi

echo "   Running plotting script..."
python "$SCRIPT_PATH" "$METRICS_FILE" "$PLOT_OUTPUT"

if [ -f "$PLOT_OUTPUT" ]; then
    echo "✅ Plot generated successfully at: $PLOT_OUTPUT"
else
    echo "❌ Script ran but output file not found."
    exit 1
fi

echo "========================================================"
echo "🎉 Done!"
echo "========================================================"
