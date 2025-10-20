#!/bin/bash
# Setup script for local AI generation

echo "========================================="
echo "KevCal Local AI Setup"
echo "========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv"
    exit 1
fi

# Activate venv
source venv/bin/activate

echo "Step 1: Detecting GPU..."
echo ""

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
    echo "Installing PyTorch with CUDA support..."
    pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu121
else
    echo "⚠ No NVIDIA GPU detected"
    echo "Installing PyTorch for CPU (will be slower)..."
    pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu
fi

echo ""
echo "Step 2: Installing AI libraries..."
echo ""

pip install diffusers==0.25.0 transformers==4.36.2 accelerate==0.25.0 safetensors==0.4.1

echo ""
echo "Step 3: Installing xformers (optional speedup)..."
echo ""

pip install xformers==0.0.23.post1 2>/dev/null || echo "⚠ xformers install failed (OK, not required)"

echo ""
echo "Step 4: Testing installation..."
echo ""

python -c "import torch; print(f'✓ PyTorch installed: {torch.__version__}'); print(f'✓ CUDA available: {torch.cuda.is_available()}')" || echo "❌ PyTorch test failed"
python -c "from diffusers import StableDiffusionXLPipeline; print('✓ Diffusers installed')" || echo "❌ Diffusers test failed"

echo ""
echo "Step 5: Configuring environment..."
echo ""

# Update .env if not already set
if ! grep -q "USE_LOCAL_AI" .env 2>/dev/null; then
    echo "USE_LOCAL_AI=true" >> .env
    echo "✓ Added USE_LOCAL_AI=true to .env"
else
    echo "✓ USE_LOCAL_AI already configured"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Models will auto-download (~7GB) on first generation"
echo "This takes 5-10 minutes depending on your connection"
echo ""
echo "Start server with: python app.py"
echo ""
echo "GPU Status:"
python -c "import torch; print(f'  CUDA: {torch.cuda.is_available()}')" 2>/dev/null || echo "  CPU only"
echo ""
echo "See SETUP_LOCAL_AI.md for detailed documentation"
echo ""
