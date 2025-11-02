#!/usr/bin/env python3
"""
Test Gemini image generation to diagnose failures
"""
import os
import sys

# Add app to path
sys.path.insert(0, '/home/peteylinux/Projects/KevCal')

from app.services.gemini_service import generate_calendar_image
from app.services.monthly_themes import get_enhanced_prompt

def test_generation():
    """Test generating a simple image"""

    print("="*70)
    print("TESTING GEMINI IMAGE GENERATION")
    print("="*70)

    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyAXdQlDioxbG3wr9jHEaFJiIt6AB5Bdals')
    print(f"\n✓ API Key configured: {api_key[:20]}...")

    # Test without reference images first
    print("\n" + "="*70)
    print("TEST 1: Simple generation (no reference images)")
    print("="*70)

    try:
        simple_prompt = "Hyper-realistic photo of a muscular shirtless male firefighter with defined abs, wearing firefighter suspenders and a helmet, spraying champagne on New Year's fireworks"
        print(f"Prompt: {simple_prompt[:100]}...")

        image_data = generate_calendar_image(simple_prompt, reference_image_data_list=None)

        if image_data:
            print(f"\n✅ SUCCESS! Generated {len(image_data)} bytes")
            with open('/tmp/test_simple.png', 'wb') as f:
                f.write(image_data)
            print(f"   Saved to: /tmp/test_simple.png")
        else:
            print("\n❌ FAILED: No image data returned")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test with enhanced prompt from monthly_themes
    print("\n" + "="*70)
    print("TEST 2: With enhanced prompt from monthly_themes")
    print("="*70)

    try:
        enhanced_prompt = get_enhanced_prompt(1)  # January
        print(f"Enhanced prompt: {enhanced_prompt[:100]}...")

        image_data = generate_calendar_image(enhanced_prompt, reference_image_data_list=None)

        if image_data:
            print(f"\n✅ SUCCESS! Generated {len(image_data)} bytes")
            with open('/tmp/test_enhanced.png', 'wb') as f:
                f.write(image_data)
            print(f"   Saved to: /tmp/test_enhanced.png")
        else:
            print("\n❌ FAILED: No image data returned")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_generation()
