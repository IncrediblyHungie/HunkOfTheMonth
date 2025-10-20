"""
Simple face overlay - extract face from source and overlay on template
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

class SimpleFaceOverlay:
    """Simple face extraction and overlay without complex face swapping"""

    def __init__(self):
        """Initialize with face detection cascade"""
        # Load OpenCV's face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def extract_face(self, image_path, padding=0.3):
        """
        Extract face region from image with padding

        Args:
            image_path: Path to source image
            padding: Extra padding around face (0.3 = 30% extra)

        Returns:
            PIL Image of extracted face, or None if no face found
        """
        # Read image
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        # Convert to grayscale for detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        if len(faces) == 0:
            return None

        # Get largest face
        face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = face

        # Add padding
        pad_w = int(w * padding)
        pad_h = int(h * padding)

        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(img.shape[1], x + w + pad_w)
        y2 = min(img.shape[0], y + h + pad_h)

        # Extract face region
        face_region = img[y1:y2, x1:x2]

        # Convert to PIL Image
        face_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
        return Image.fromarray(face_rgb)

    def overlay_face_on_template(self, source_image_path, template_image_path, output_path,
                                 position="center", size=(400, 400)):
        """
        Overlay extracted face onto template image

        Args:
            source_image_path: Path to source image with face
            template_image_path: Path to template/background image
            output_path: Path to save result
            position: Where to place face ("center", "top", "custom")
            size: Size of face overlay (width, height)
        """
        # Extract face from source
        face_img = self.extract_face(source_image_path)

        if face_img is None:
            # No face found, just use template
            template = Image.open(template_image_path)
            template.save(output_path, quality=95)
            return output_path

        # Open template
        template = Image.open(template_image_path).convert('RGBA')

        # Resize face to target size
        face_img = face_img.convert('RGBA')
        face_img = face_img.resize(size, Image.Resampling.LANCZOS)

        # Create circular mask for better blending
        mask = Image.new('L', size, 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, size[0], size[1]], fill=255)

        # Apply mask to face
        face_with_mask = Image.new('RGBA', size, (0, 0, 0, 0))
        face_with_mask.paste(face_img, (0, 0))

        # Create alpha mask
        alpha = face_with_mask.split()[3]
        alpha = Image.composite(mask, Image.new('L', size, 0), alpha)
        face_with_mask.putalpha(alpha)

        # Calculate position
        if position == "center":
            x = (template.width - size[0]) // 2
            y = (template.height - size[1]) // 2 - 200  # Slightly above center
        elif position == "top":
            x = (template.width - size[0]) // 2
            y = 200
        else:
            x, y = position  # Custom position tuple

        # Paste face onto template
        template.paste(face_with_mask, (x, y), face_with_mask)

        # Convert back to RGB and save
        result = template.convert('RGB')
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result.save(output_path, quality=95)

        return output_path

    def batch_overlay(self, source_image_path, template_paths, output_dir,
                     position="center", size=(400, 400)):
        """
        Overlay face onto multiple templates

        Args:
            source_image_path: Path to source image
            template_paths: List of template image paths
            output_dir: Directory to save results
            position: Face position on templates
            size: Face size

        Returns:
            List of output paths
        """
        output_paths = []

        for i, template_path in enumerate(template_paths):
            output_name = f"overlay_{i+1}_{Path(template_path).name}"
            output_path = Path(output_dir) / output_name

            try:
                self.overlay_face_on_template(
                    source_image_path,
                    template_path,
                    str(output_path),
                    position=position,
                    size=size
                )
                output_paths.append(str(output_path))
                print(f"✓ Created overlay {i+1}/{len(template_paths)}")
            except Exception as e:
                print(f"✗ Failed overlay on {template_path}: {e}")

        return output_paths
