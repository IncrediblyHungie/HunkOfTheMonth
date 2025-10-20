#!/usr/bin/env python3
"""
Test script for local AI generation
Generates a single test image to verify setup
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.local_ai_generator import LocalAIGenerator

def test_generation():
    """Test local AI generation"""

    print("=" * 60)
    print("KevCal Local AI Test")
    print("=" * 60)
    print()

    # Initialize generator
    print("Initializing AI generator...")
    generator = LocalAIGenerator(method="auto")

    if not generator.enabled:
        print()
        print("❌ Local AI not available!")
        print()
        print("Possible reasons:")
        print("1. PyTorch not installed: pip install torch")
        print("2. Diffusers not installed: pip install diffusers")
        print("3. No GPU and CPU generation not enabled")
        print()
        print("Run: ./setup_local_ai.sh")
        return False

    print(f"✓ Generator initialized")
    print(f"  Method: {generator.method}")
    print(f"  Device: {generator.device}")
    print()

    # Test prompt
    test_prompt = (
        "Shirtless muscular firefighter with defined abs, wearing firefighter pants "
        "and suspenders, holding axe, standing heroically in front of burning building "
        "with flames and smoke, dramatic orange lighting, professional photography"
    )

    output_path = "output/test_firefighter.jpg"

    print("Generating test image...")
    print(f"Prompt: {test_prompt[:80]}...")
    print()
    print("This will take:")
    print("  - First run: 5-15 minutes (downloading models)")
    print("  - GPU: 5-15 seconds per image")
    print("  - CPU: 2-5 minutes per image")
    print()

    try:
        result = generator.generate_themed_image(
            test_prompt,
            "Test Firefighter",
            output_path
        )

        if result:
            print()
            print("=" * 60)
            print("✓ SUCCESS!")
            print("=" * 60)
            print()
            print(f"Test image saved: {result}")
            print()
            print("Your local AI is working correctly!")
            print("You can now generate unlimited calendars for free.")
            print()
            return True
        else:
            print()
            print("❌ Generation failed")
            return False

    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_generation()
    sys.exit(0 if success else 1)
