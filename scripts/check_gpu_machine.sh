#!/bin/bash
# GPU Machine Info Collector for GitHub Actions Self-Hosted Runner Setup

echo "=========================================="
echo "GPU Machine Information Report"
echo "=========================================="
echo ""

echo "1. SYSTEM INFORMATION"
echo "---------------------"
echo "OS: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
if [ -f /etc/os-release ]; then
    echo "Distribution:"
    cat /etc/os-release | grep -E "^(NAME|VERSION)="
fi
echo ""

echo "2. GPU INFORMATION"
echo "------------------"
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo ""
    echo "Full nvidia-smi output:"
    nvidia-smi
else
    echo "⚠️  nvidia-smi not found. Checking for GPU via lspci..."
    if command -v lspci &> /dev/null; then
        lspci | grep -i "vga\|3d\|display"
    else
        echo "❌ No GPU detection tools available"
    fi
fi
echo ""

echo "3. CUDA INFORMATION"
echo "-------------------"
if command -v nvcc &> /dev/null; then
    echo "CUDA Compiler (nvcc):"
    nvcc --version
else
    echo "⚠️  nvcc not found"
fi

if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "CUDA Version from nvidia-smi:"
    nvidia-smi | grep "CUDA Version" || echo "Not available"
fi
echo ""

echo "4. PYTHON INFORMATION"
echo "---------------------"
if command -v python3 &> /dev/null; then
    echo "Python3 path: $(which python3)"
    echo "Python3 version: $(python3 --version)"
    
    # Check for PyTorch
    if python3 -c "import torch" 2>/dev/null; then
        echo ""
        echo "PyTorch detected:"
        python3 -c "import torch; print(f'  Version: {torch.__version__}'); print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
    else
        echo "⚠️  PyTorch not installed"
    fi
else
    echo "❌ Python3 not found"
fi
echo ""

echo "5. DISK SPACE"
echo "-------------"
df -h / | tail -n 1
echo ""

echo "6. MEMORY"
echo "---------"
if command -v free &> /dev/null; then
    free -h | grep -E "^(Mem|Swap)"
else
    echo "⚠️  'free' command not available"
fi
echo ""

echo "7. NETWORK CONNECTIVITY"
echo "-----------------------"
if curl -s -I https://github.com -m 5 | head -n 1; then
    echo "✅ GitHub is reachable"
else
    echo "❌ Cannot reach GitHub"
fi
echo ""

echo "8. DOCKER (Optional for containerized runners)"
echo "-----------------------------------------------"
if command -v docker &> /dev/null; then
    echo "Docker version: $(docker --version)"
    echo "Docker running: $(docker ps &>/dev/null && echo 'Yes' || echo 'No (needs sudo or not running)')"
else
    echo "⚠️  Docker not installed"
fi
echo ""

echo "=========================================="
echo "Report Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy this entire output"
echo "2. Send it to configure the GitHub Actions runner"
echo "3. We'll set up PyTorch with CUDA support"
