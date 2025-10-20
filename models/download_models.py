"""
Script to download InsightFace models

This script downloads the required models for face detection and analysis.
Models will be cached in ~/.insightface/models/
"""
import os
from insightface.app import FaceAnalysis

def download_models():
    """Download InsightFace buffalo_l model"""
    print("Downloading InsightFace models...")
    print("This may take a few minutes on first run.")
    print()

    try:
        # Initialize FaceAnalysis - this will download models if not present
        app = FaceAnalysis(name='buffalo_l')

        print("✓ Models downloaded successfully!")
        print(f"✓ Models cached in: ~/.insightface/models/")
        print()
        print("You can now run the application with: python app.py")

    except Exception as e:
        print(f"✗ Failed to download models: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Try running with sudo if permission errors occur")
        print("3. Manually download from: https://github.com/deepinsight/insightface")

if __name__ == "__main__":
    download_models()
