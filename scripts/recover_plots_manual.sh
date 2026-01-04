#!/bin/bash
set -e  # Exit on error

# Configuration
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
PROJECT_ROOT="$(pwd)/blokus-engine" # Assuming script is run from repo root
EXPERIMENT_PATH="/projects/ctb/blokus-runner/_work/Blokus/Blokus/blokus-engine/models/experiments/duo_gpu_2h_run_v1_20260104_211851"
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
    echo "   Python: $(which python)"
    echo "   Version: $(python --version)"
else
    echo "❌ Venv NOT found at $VENV_DIR"
    exit 1
fi

echo "--------------------------------------------------------"
echo "📦 Checking Dependencies..."

# Check if matplotlib is installed
if python -c "import matplotlib" 2>/dev/null; then
    echo "✅ Matplotlib is already installed."
else
    echo "⚠️  Matplotlib not found. Installing dependencies..."
    
    # Navigate to engine to install deps
    if [ -d "blokus-engine" ]; then
        cd blokus-engine
        echo "   Changed directory to blokus-engine"
    elif [ -f "pyproject.toml" ]; then
        echo "   Already in what looks like the engine/project root"
    else
        echo "❌ Could not find blokus-engine directory or pyproject.toml"
        exit 1
    fi

    echo "   Running pip install -e '.[dev]'..."
    pip install -e ".[dev]"
    echo "✅ Dependencies updated."
    
    # Return to original dir if needed, but we probably just want to run the script now
    cd ..
fi

echo "--------------------------------------------------------"
echo "📈 Generating Plot..."
echo "Target: $METRICS_FILE"

if [ -f "$METRICS_FILE" ]; then
    echo "   Metrics file exists."
    
    # Determine path to plot_metrics.py
    SCRIPT_PATH="blokus-engine/scripts/plot_metrics.py"
    if [ ! -f "$SCRIPT_PATH" ]; then
        SCRIPT_PATH="scripts/plot_metrics.py" # try relative if inside engine
    fi
    
    if [ ! -f "$SCRIPT_PATH" ]; then
         echo "❌ Could not find plot_metrics.py at $SCRIPT_PATH"
         find . -name "plot_metrics.py"
         exit 1
    fi

    echo "   Running: python $SCRIPT_PATH \"$METRICS_FILE\" \"$PLOT_OUTPUT\""
    python "$SCRIPT_PATH" "$METRICS_FILE" "$PLOT_OUTPUT"
    
    if [ -f "$PLOT_OUTPUT" ]; then
        echo "✅ Plot generated successfully at: $PLOT_OUTPUT"
    else
        echo "❌ Script ran but output file not found."
        exit 1
    fi
else
    echo "❌ Metrics file not found!"
    ls -l "$EXPERIMENT_PATH"
    exit 1
fi

echo "========================================================"
echo "🎉 Done! You can now commit the result if you are in the git repo."
echo "========================================================"
