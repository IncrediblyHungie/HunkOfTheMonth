"""
AI Image Generation using Replicate API
Generates themed bodybuilder/hunk images for calendar
"""
import os
import requests
import time
from pathlib import Path
import replicate

class AIImageGenerator:
    """Generate themed images using AI (Stable Diffusion via Replicate)"""

    def __init__(self, api_token=None):
        """Initialize with Replicate API token"""
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            print("Warning: No REPLICATE_API_TOKEN found. AI generation will be skipped.")
            self.enabled = False
        else:
            self.enabled = True
            os.environ['REPLICATE_API_TOKEN'] = self.api_token

    def generate_themed_image(self, theme_description, theme_name, output_path, negative_prompt=None):
        """
        Generate a themed image based on description

        Args:
            theme_description: Description of the scene/theme
            theme_name: Name of theme for filename
            output_path: Where to save generated image
            negative_prompt: Things to avoid in image

        Returns:
            Path to generated image
        """
        if not self.enabled:
            print(f"AI generation disabled for {theme_name}")
            return None

        # Enhanced prompt for muscular/attractive subject
        enhanced_prompt = self._create_enhanced_prompt(theme_description, theme_name)

        # Default negative prompt
        if not negative_prompt:
            negative_prompt = (
                "ugly, deformed, noisy, blurry, low contrast, text, watermark, "
                "signature, multiple people, crowd, bad anatomy, bad proportions, "
                "extra limbs, cloned face, disfigured, gross proportions, malformed limbs"
            )

        print(f"Generating AI image for {theme_name}...")
        print(f"Prompt: {enhanced_prompt[:100]}...")

        try:
            # Use Stable Diffusion XL for high quality
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": enhanced_prompt,
                    "negative_prompt": negative_prompt,
                    "width": 1024,
                    "height": 1024,
                    "num_outputs": 1,
                    "scheduler": "DPMSolverMultistep",
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                    "refine": "expert_ensemble_refiner",
                    "high_noise_frac": 0.8
                }
            )

            # Download generated image
            if output and len(output) > 0:
                image_url = output[0]
                print(f"Downloading generated image from {image_url}...")

                response = requests.get(image_url, timeout=60)
                response.raise_for_status()

                # Save image
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                print(f"✓ Generated image saved: {output_path}")
                return output_path

        except Exception as e:
            print(f"✗ AI generation failed for {theme_name}: {e}")
            return None

    def _create_enhanced_prompt(self, base_description, theme_name):
        """
        Create enhanced prompt for muscular/attractive themed image

        Args:
            base_description: Base theme description
            theme_name: Theme name

        Returns:
            Enhanced prompt string
        """
        # Base quality tags
        quality_tags = (
            "professional photography, 8k uhd, high quality, detailed, "
            "dramatic lighting, cinematic composition, sharp focus"
        )

        # Body/physique tags
        physique_tags = (
            "muscular athletic male, handsome, strong jawline, "
            "fit physique, heroic pose, confident expression"
        )

        # Combine into complete prompt
        full_prompt = f"{base_description}, {physique_tags}, {quality_tags}"

        return full_prompt

    def generate_calendar_set(self, themes, output_dir):
        """
        Generate complete set of 12 themed images

        Args:
            themes: List of theme dictionaries with 'description' and 'name'
            output_dir: Directory to save images

        Returns:
            List of generated image paths
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        generated_paths = []

        for i, theme in enumerate(themes, 1):
            month = theme.get('month', i)
            theme_name = theme.get('theme', f'Theme {i}')
            description = theme.get('description', '')

            # Output filename
            filename = f"{month:02d}_{theme_name.lower().replace(' ', '_')}_ai.jpg"
            output_path = Path(output_dir) / filename

            # Generate image
            result_path = self.generate_themed_image(
                description,
                theme_name,
                str(output_path)
            )

            if result_path:
                generated_paths.append(result_path)
            else:
                generated_paths.append(None)

            # Rate limiting - wait between generations
            if i < len(themes):
                print(f"Waiting before next generation... ({i}/{len(themes)})")
                time.sleep(2)

        return generated_paths


# Enhanced theme descriptions for muscular/hunk bodies
ENHANCED_CALENDAR_THEMES = [
    {
        "month": 1,
        "name": "January",
        "theme": "Firefighter",
        "ai_prompt": "Shirtless muscular firefighter with defined abs, wearing firefighter pants and suspenders, holding axe, standing heroically in front of burning building with flames and smoke, dramatic orange lighting, intense expression, safety helmet"
    },
    {
        "month": 2,
        "name": "February",
        "theme": "Fighter Pilot",
        "ai_prompt": "Handsome muscular fighter pilot in open flight suit showing muscular chest, sitting in F-16 cockpit, wearing aviator sunglasses, helmet nearby, instrument panels visible, confident smirk, golden hour lighting"
    },
    {
        "month": 3,
        "name": "March",
        "theme": "Astronaut",
        "ai_prompt": "Athletic astronaut in fitted white NASA space suit unzipped to show muscular chest, floating in international space station, Earth visible through window, zero gravity, professional photography, futuristic lighting"
    },
    {
        "month": 4,
        "name": "April",
        "theme": "Cowboy",
        "ai_prompt": "Shirtless muscular cowboy with six-pack abs wearing worn jeans and cowboy hat, on horseback at golden sunset, leather vest open, western landscape, rugged masculine features, warm orange glow"
    },
    {
        "month": 5,
        "name": "May",
        "theme": "Chef",
        "ai_prompt": "Handsome shirtless chef with muscular torso wearing white chef's hat and apron, cooking with flames in gourmet kitchen, professional knife in hand, confident smile, dramatic fire lighting, culinary passion"
    },
    {
        "month": 6,
        "name": "June",
        "theme": "Rock Star",
        "ai_prompt": "Shirtless muscular rock star guitarist with defined abs and tattoos, playing electric guitar on stage, dramatic purple and red concert lighting, crowd silhouettes, leather pants, long hair, rockstar attitude"
    },
    {
        "month": 7,
        "name": "July",
        "theme": "Deep Sea Diver",
        "ai_prompt": "Athletic diver in partially unzipped wetsuit showing muscular chest, underwater surrounded by colorful coral reef and tropical fish, holding diving equipment, blue filtered sunlight, underwater photography"
    },
    {
        "month": 8,
        "name": "August",
        "theme": "Mountain Climber",
        "ai_prompt": "Shirtless muscular mountain climber with climbing harness and ropes, standing at snowy mountain summit, defined muscles glistening, ice axe in hand, dramatic mountain vista, victory pose, golden hour"
    },
    {
        "month": 9,
        "name": "September",
        "theme": "Race Car Driver",
        "ai_prompt": "Handsome muscular Formula 1 driver with racing suit unzipped to waist showing six-pack abs, sitting in red F1 car, racing helmet under arm, pit lane background, confident pose, motorsport photography"
    },
    {
        "month": 10,
        "name": "October",
        "theme": "Samurai Warrior",
        "ai_prompt": "Shirtless muscular samurai warrior showing defined chest and abs, wearing traditional hakama pants, holding katana sword, cherry blossoms falling, Japanese temple background, dramatic side lighting, warrior stance"
    },
    {
        "month": 11,
        "name": "November",
        "theme": "Viking Warrior",
        "ai_prompt": "Muscular shirtless viking warrior with long beard and battle scars, wearing fur cape and leather armor, holding shield and battle axe, on viking longship, stormy seas, dramatic lighting, nordic warrior"
    },
    {
        "month": 12,
        "name": "December",
        "theme": "Secret Agent",
        "ai_prompt": "Handsome muscular secret agent in unbuttoned black tuxedo showing muscular chest, holding silenced pistol, elegant casino background, dramatic noir lighting, bow tie loose, james bond style, sophisticated danger"
    }
]
