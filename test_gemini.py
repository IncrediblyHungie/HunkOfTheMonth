"""
Test script to verify Gemini API key and image generation
"""
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAXdQlDioxbG3wr9jHEaFJiIt6AB5Bdals'

try:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key='AIzaSyAXdQlDioxbG3wr9jHEaFJiIt6AB5Bdals')

    # Test simple image generation
    prompt = "A photorealistic portrait of a muscular firefighter, shirtless, heroic pose"

    print("Testing Gemini 2.5 Flash Image API...")
    print(f"Prompt: {prompt}")

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )
    )

    print("✅ API Key is valid!")
    print(f"Response received: {type(response)}")

    # Check if we got image data
    if hasattr(response, 'candidates') and response.candidates:
        print(f"Number of candidates: {len(response.candidates)}")

        # Save the generated image
        for i, candidate in enumerate(response.candidates):
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        with open(f'test_output_{i}.png', 'wb') as f:
                            f.write(image_data)
                        print(f"✅ Saved test image to: test_output_{i}.png")
                        print(f"   Image size: {len(image_data)} bytes")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Need to install: pip install google-genai")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
