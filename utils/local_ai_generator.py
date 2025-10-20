"""
Local AI Image Generation using Stable Diffusion
Supports both direct diffusers and ComfyUI API
"""
import os
import torch
from pathlib import Path
import requests
import json
import time

class LocalAIGenerator:
    """Generate images locally using Stable Diffusion"""

    def __init__(self, method="auto", comfyui_url=None):
        """
        Initialize local AI generator

        Args:
            method: "diffusers", "comfyui", or "auto" (tries diffusers first)
            comfyui_url: URL to ComfyUI API (e.g., http://localhost:8188)
        """
        self.method = method
        self.comfyui_url = comfyui_url or os.getenv('COMFYUI_URL', 'http://localhost:8188')
        self.enabled = False
        self.pipeline = None
        self.device = "cpu"

        # Try to initialize based on method
        if method == "auto":
            if self._try_init_diffusers():
                self.method = "diffusers"
                self.enabled = True
            elif self._check_comfyui():
                self.method = "comfyui"
                self.enabled = True
        elif method == "diffusers":
            if self._try_init_diffusers():
                self.enabled = True
        elif method == "comfyui":
            if self._check_comfyui():
                self.enabled = True

        print(f"Local AI Generator: method={self.method}, enabled={self.enabled}")

    def _try_init_diffusers(self):
        """Try to initialize diffusers pipeline"""
        try:
            from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

            # Check for CUDA
            if torch.cuda.is_available():
                self.device = "cuda"
                print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                print("⚠ No CUDA, using CPU (will be slow)")

            print("Loading Stable Diffusion XL model...")
            print("This will download ~7GB on first run, please wait...")

            # Load SDXL model (optimized for speed)
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"

            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                variant="fp16" if self.device == "cuda" else None
            )

            self.pipeline.to(self.device)

            # Optimize for speed
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )

            # Enable optimizations
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()
                # Try to enable xformers if available
                try:
                    self.pipeline.enable_xformers_memory_efficient_attention()
                    print("✓ xformers enabled for faster generation")
                except:
                    print("⚠ xformers not available, using standard attention")

            print("✓ Stable Diffusion XL loaded successfully!")
            return True

        except ImportError as e:
            print(f"⚠ Diffusers not available: {e}")
            return False
        except Exception as e:
            print(f"⚠ Failed to load diffusers: {e}")
            return False

    def _check_comfyui(self):
        """Check if ComfyUI is running and accessible"""
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats", timeout=2)
            if response.status_code == 200:
                print(f"✓ ComfyUI detected at {self.comfyui_url}")
                return True
        except:
            pass

        print(f"⚠ ComfyUI not accessible at {self.comfyui_url}")
        return False

    def generate_image_diffusers(self, prompt, negative_prompt, output_path):
        """Generate image using diffusers pipeline"""
        if not self.pipeline:
            raise RuntimeError("Diffusers pipeline not initialized")

        print(f"Generating with diffusers on {self.device}...")

        # Generate image
        image = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=20,  # Reduced for speed (30 is better quality)
            guidance_scale=7.5,
            width=1024,
            height=1024
        ).images[0]

        # Save
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)

        print(f"✓ Image saved: {output_path}")
        return output_path

    def generate_image_comfyui(self, prompt, negative_prompt, output_path):
        """Generate image using ComfyUI API"""

        # ComfyUI workflow JSON (simplified)
        workflow = {
            "prompt": {
                "3": {
                    "class_type": "KSampler",
                    "inputs": {
                        "seed": int(time.time()),
                        "steps": 20,
                        "cfg": 7.5,
                        "sampler_name": "dpmpp_2m",
                        "scheduler": "karras",
                        "denoise": 1.0,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0]
                    }
                },
                "4": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
                },
                "5": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
                },
                "6": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": prompt, "clip": ["4", 1]}
                },
                "7": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": negative_prompt, "clip": ["4", 1]}
                },
                "8": {
                    "class_type": "VAEDecode",
                    "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
                },
                "9": {
                    "class_type": "SaveImage",
                    "inputs": {"filename_prefix": "kevcal", "images": ["8", 0]}
                }
            }
        }

        # Queue prompt
        try:
            response = requests.post(
                f"{self.comfyui_url}/prompt",
                json=workflow,
                timeout=5
            )
            response.raise_for_status()

            prompt_id = response.json()['prompt_id']
            print(f"ComfyUI generation started: {prompt_id}")

            # Poll for completion
            max_wait = 300  # 5 minutes
            start_time = time.time()

            while time.time() - start_time < max_wait:
                history_response = requests.get(f"{self.comfyui_url}/history/{prompt_id}")

                if history_response.status_code == 200:
                    history = history_response.json()

                    if prompt_id in history:
                        # Get output image
                        outputs = history[prompt_id].get('outputs', {})

                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                for img in node_output['images']:
                                    filename = img['filename']
                                    subfolder = img.get('subfolder', '')

                                    # Download image
                                    img_url = f"{self.comfyui_url}/view?filename={filename}&subfolder={subfolder}"
                                    img_response = requests.get(img_url)

                                    if img_response.status_code == 200:
                                        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                                        with open(output_path, 'wb') as f:
                                            f.write(img_response.content)

                                        print(f"✓ Image downloaded from ComfyUI: {output_path}")
                                        return output_path

                time.sleep(2)

            raise TimeoutError("ComfyUI generation timed out")

        except Exception as e:
            raise RuntimeError(f"ComfyUI generation failed: {e}")

    def generate_themed_image(self, theme_description, theme_name, output_path, negative_prompt=None):
        """
        Generate themed image using available method

        Args:
            theme_description: Description/prompt for the image
            theme_name: Name of the theme
            output_path: Where to save the image
            negative_prompt: Things to avoid

        Returns:
            Path to generated image or None if failed
        """
        if not self.enabled:
            print(f"⚠ Local AI disabled for {theme_name}")
            return None

        # Default negative prompt
        if not negative_prompt:
            negative_prompt = (
                "ugly, deformed, noisy, blurry, low contrast, text, watermark, "
                "signature, multiple people, crowd, bad anatomy, bad proportions, "
                "extra limbs, cloned face, disfigured, gross proportions"
            )

        # Enhanced prompt with quality tags
        quality_tags = (
            "professional photography, 8k uhd, high quality, detailed, "
            "dramatic lighting, cinematic composition, sharp focus, "
            "muscular athletic male, handsome, strong jawline, fit physique, "
            "heroic pose, confident expression"
        )

        full_prompt = f"{theme_description}, {quality_tags}"

        print(f"\n=== Generating {theme_name} ===")
        print(f"Method: {self.method}")
        print(f"Prompt: {full_prompt[:100]}...")

        try:
            if self.method == "diffusers":
                return self.generate_image_diffusers(full_prompt, negative_prompt, output_path)
            elif self.method == "comfyui":
                return self.generate_image_comfyui(full_prompt, negative_prompt, output_path)
            else:
                print(f"⚠ Unknown method: {self.method}")
                return None

        except Exception as e:
            print(f"✗ Generation failed for {theme_name}: {e}")
            return None

    def batch_generate(self, themes, output_dir):
        """
        Generate multiple themed images

        Args:
            themes: List of theme dicts with 'ai_prompt', 'theme', 'month'
            output_dir: Directory to save images

        Returns:
            List of generated image paths
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        generated_paths = []

        for i, theme in enumerate(themes, 1):
            month = theme.get('month', i)
            theme_name = theme.get('theme', f'Theme {i}')
            prompt = theme.get('ai_prompt', theme.get('description', ''))

            filename = f"{month:02d}_{theme_name.lower().replace(' ', '_')}_local.jpg"
            output_path = Path(output_dir) / filename

            result = self.generate_themed_image(prompt, theme_name, str(output_path))

            if result:
                generated_paths.append(result)
            else:
                generated_paths.append(None)

            print(f"Progress: {i}/{len(themes)}")

        return generated_paths
