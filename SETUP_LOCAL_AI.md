# Local AI Generation Setup Guide

## Overview

Run Stable Diffusion locally on your machine instead of using Replicate API. This gives you:

✅ **No API costs** - Generate unlimited calendars for free
✅ **No rate limits** - Generate as fast as your GPU allows
✅ **Privacy** - Images never leave your machine
✅ **Customization** - Use any Stable Diffusion model
✅ **Offline** - Works without internet connection

## Hardware Requirements

### Minimum (CPU Only)
- **RAM**: 16GB+ recommended
- **Storage**: 10GB for models
- **Speed**: ~2-5 minutes per image
- **Quality**: Full quality

### Recommended (GPU)
- **GPU**: NVIDIA with 6GB+ VRAM (RTX 3060, 4060, or better)
- **RAM**: 16GB
- **Storage**: 10GB for models
- **Speed**: ~5-15 seconds per image
- **Quality**: Full quality with optimizations

### Optimal (High-end GPU)
- **GPU**: NVIDIA with 12GB+ VRAM (RTX 4080, 4090, A6000)
- **RAM**: 32GB
- **Storage**: 10GB for models
- **Speed**: ~3-8 seconds per image
- **Quality**: Maximum quality with all optimizations

## Installation Methods

### Method 1: Direct Diffusers (Recommended - Simpler)

This uses the diffusers library directly in Python. No separate software needed.

#### Step 1: Install PyTorch

**For NVIDIA GPU (CUDA):**
```bash
source venv/bin/activate
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu121
```

**For CPU only:**
```bash
source venv/bin/activate
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cpu
```

**For AMD GPU (ROCm) on Linux:**
```bash
source venv/bin/activate
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/rocm5.7
```

#### Step 2: Install AI Libraries

```bash
pip install diffusers==0.25.0 transformers==4.36.2 accelerate==0.25.0 safetensors==0.4.1
```

#### Step 3: Install xformers (Optional - Faster on NVIDIA)

```bash
pip install xformers==0.0.23.post1
```

If xformers install fails, skip it. The system will work without it, just slightly slower.

#### Step 4: Test Installation

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "from diffusers import StableDiffusionXLPipeline; print('Diffusers OK')"
```

#### Step 5: Download Models (First Run)

The system will auto-download ~7GB of models on first generation:
- Stable Diffusion XL base model
- CLIP text encoders
- VAE decoder

This happens automatically, just takes 5-10 minutes on first run.

#### Step 6: Enable in .env

```bash
echo 'USE_LOCAL_AI=true' >> .env
```

#### Step 7: Restart Server

```bash
python app.py
```

Look for: `✓ Stable Diffusion XL loaded successfully!`

### Method 2: ComfyUI (Advanced - More Control)

ComfyUI is a powerful node-based interface for Stable Diffusion. Use this if you want maximum control.

#### Step 1: Install ComfyUI

```bash
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python -m venv venv_comfy
source venv_comfy/bin/activate
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

#### Step 2: Download SDXL Model

```bash
cd ~/ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

#### Step 3: Start ComfyUI Server

```bash
cd ~/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

#### Step 4: Configure KevCal

```bash
# In KevCal .env file:
USE_LOCAL_AI=true
COMFYUI_URL=http://localhost:8188
```

#### Step 5: Restart KevCal

```bash
cd /home/peteylinux/Projects/KevCal
python app.py
```

Look for: `✓ ComfyUI detected at http://localhost:8188`

## Configuration Options

### Environment Variables

```bash
# Enable local AI (default: true)
USE_LOCAL_AI=true

# ComfyUI URL if using ComfyUI method
COMFYUI_URL=http://localhost:8188

# Disable local AI and use Replicate instead
USE_LOCAL_AI=false
REPLICATE_API_TOKEN=r8_...
```

### Generation Settings

Edit `utils/local_ai_generator.py` to tune generation:

```python
# Line ~98: Adjust quality vs speed
num_inference_steps=20  # 20=fast, 30=better quality, 50=best quality

# Line ~99: Adjust prompt adherence
guidance_scale=7.5  # 7.5=balanced, 10=more literal, 5=more creative

# Line ~100-101: Adjust resolution
width=1024   # Higher = better detail but slower
height=1024
```

## Performance Benchmarks

### NVIDIA RTX 4080 (16GB VRAM)
- **Per image**: 5-8 seconds
- **12 images**: ~1-2 minutes
- **Quality**: Maximum

### NVIDIA RTX 3060 (12GB VRAM)
- **Per image**: 10-15 seconds
- **12 images**: ~2-3 minutes
- **Quality**: Maximum

### NVIDIA RTX 3060 (6GB VRAM)
- **Per image**: 15-25 seconds
- **12 images**: ~3-5 minutes
- **Quality**: High (with optimizations)

### CPU Only (16GB RAM)
- **Per image**: 2-5 minutes
- **12 images**: ~30-60 minutes
- **Quality**: Maximum

## Usage

### Generate Calendar with Local AI

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Check AI status**:
   ```bash
   curl http://localhost:8000/api/ai-status
   ```

   Should show:
   ```json
   {
     "ai_enabled": true,
     "method": "diffusers",
     "device": "cuda"
   }
   ```

3. **Generate calendar**:
   - Open http://localhost:8000
   - Upload photos
   - Click "Generate Calendar Images"
   - Watch console for progress:
     ```
     === Generating Firefighter ===
     Method: diffusers
     ✓ Image saved: output/.../01_firefighter_local.jpg
     ```

### First Generation Takes Longer

The first time you generate:
1. Models download (~7GB, 5-10 minutes)
2. Models load into memory (~30 seconds)
3. Image generation begins

Subsequent generations are much faster!

## Troubleshooting

### Out of Memory Error

**Symptom**: `RuntimeError: CUDA out of memory`

**Solutions**:
```python
# Edit utils/local_ai_generator.py

# Option 1: Reduce resolution
width=768, height=768  # Instead of 1024x1024

# Option 2: Enable CPU offloading
self.pipeline.enable_model_cpu_offload()

# Option 3: Use less steps
num_inference_steps=15  # Instead of 20
```

### Slow Generation (CPU)

**Symptom**: Each image takes 3+ minutes

**This is normal for CPU!** Options:
1. Use GPU (much faster)
2. Reduce steps to 15
3. Use smaller model (SD 1.5 instead of SDXL)
4. Use Replicate API instead

### Models Won't Download

**Symptom**: Download errors or timeouts

**Solutions**:
```bash
# Manual download
huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0 --local-dir ~/.cache/huggingface/

# Or use different mirror
export HF_ENDPOINT=https://hf-mirror.com
```

### xformers Won't Install

**This is OK!** xformers is optional. System works without it, just 10-20% slower.

## Model Selection

### Included: SDXL Base (Default)
- **Size**: 6.9GB
- **Quality**: Excellent
- **Speed**: Fast
- **Recommended**: Yes

### Alternative: SD 1.5
```python
# Edit utils/local_ai_generator.py line ~47
model_id = "runwayml/stable-diffusion-v1-5"  # Instead of SDXL
```
- **Size**: 4GB
- **Quality**: Good
- **Speed**: Faster
- **Recommended**: For low VRAM (4-6GB)

### Alternative: Custom Models
Put custom models in `~/.cache/huggingface/`:
```python
model_id = "/path/to/your/custom_model.safetensors"
```

## Cost Comparison

### Local AI (This Setup)
- **Hardware**: One-time cost (GPU if needed)
- **Per calendar**: $0.00
- **Unlimited**: ✅
- **Setup time**: 30 minutes
- **Break-even**: After ~20 calendars vs Replicate

### Replicate API
- **Hardware**: None needed
- **Per calendar**: ~$0.05
- **Unlimited**: ❌ (pay per use)
- **Setup time**: 2 minutes
- **Best for**: Testing, low volume

### Printful Costs (Same for Both)
- **Mockup generation**: Free
- **Actual calendar printing**: $15-25 each

## Advanced: Multiple GPUs

If you have multiple GPUs:

```python
# Edit utils/local_ai_generator.py
self.device = "cuda:0"  # Use specific GPU
# Or
self.device = "cuda:1"  # Use second GPU
```

## Integration with Existing Workflow

The system automatically:
1. ✅ Tries local AI first (if USE_LOCAL_AI=true)
2. ✅ Falls back to Replicate if local fails
3. ✅ Falls back to placeholder if both fail
4. ✅ Shows progress in console and UI
5. ✅ Works with same face overlay system
6. ✅ Uploads to Printful same way

No code changes needed - just install dependencies and enable!

## Next Steps

1. ✅ Install PyTorch for your hardware
2. ✅ Install diffusers and dependencies
3. ✅ Set USE_LOCAL_AI=true
4. ✅ Start server and test
5. ✅ Generate your first AI calendar locally!

## Support

- **CUDA issues**: Check NVIDIA driver version
- **ROCm issues**: AMD GPU support varies by model
- **Mac M1/M2**: Use `device="mps"` for Metal acceleration
- **ComfyUI**: Join ComfyUI Discord for help

---

**Local AI = Unlimited free generation!** 🚀
