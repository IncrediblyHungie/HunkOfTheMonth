"""
Face swap functionality using InsightFace
"""
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import os
from pathlib import Path

class FaceSwapper:
    def __init__(self):
        """Initialize face analysis model"""
        self.app = FaceAnalysis(name='buffalo_l')
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def get_face_embedding(self, image_path):
        """Extract face embedding from source image"""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        faces = self.app.get(img)
        if len(faces) == 0:
            raise ValueError("No face detected in source image")

        # Return the first face (largest by default)
        return faces[0]

    def swap_face(self, source_image_path, target_image_path, output_path):
        """
        Swap face from source image onto target image

        Args:
            source_image_path: Path to image with face to copy
            target_image_path: Path to template/target image
            output_path: Path to save result
        """
        # Load images
        source_img = cv2.imread(str(source_image_path))
        target_img = cv2.imread(str(target_image_path))

        if source_img is None:
            raise ValueError(f"Could not load source image: {source_image_path}")
        if target_img is None:
            raise ValueError(f"Could not load target image: {target_image_path}")

        # Get face from source
        source_faces = self.app.get(source_img)
        if len(source_faces) == 0:
            raise ValueError("No face detected in source image")
        source_face = source_faces[0]

        # Get faces from target
        target_faces = self.app.get(target_img)
        if len(target_faces) == 0:
            raise ValueError("No face detected in target image")

        # Simple face swap using feature alignment
        # This is a simplified version - for production, use a proper face swap model
        result_img = self._simple_face_blend(source_face, target_faces[0], source_img, target_img)

        # Save result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(str(output_path), result_img)

        return output_path

    def _simple_face_blend(self, source_face, target_face, source_img, target_img):
        """
        Simple face blending using landmark alignment
        Note: This is a basic implementation. For production, use proper face swap models.
        """
        # Get face bounding boxes
        src_bbox = source_face.bbox.astype(int)
        tgt_bbox = target_face.bbox.astype(int)

        # Extract face regions
        src_x1, src_y1, src_x2, src_y2 = src_bbox
        tgt_x1, tgt_y1, tgt_x2, tgt_y2 = tgt_bbox

        # Extract source face
        source_face_region = source_img[src_y1:src_y2, src_x1:src_x2]

        # Resize source face to match target face size
        target_face_size = (tgt_x2 - tgt_x1, tgt_y2 - tgt_y1)
        resized_source_face = cv2.resize(source_face_region, target_face_size)

        # Create a copy of target image
        result = target_img.copy()

        # Create a mask for smooth blending
        mask = np.ones(resized_source_face.shape[:2], dtype=np.float32)
        center = ((tgt_x1 + tgt_x2) // 2, (tgt_y1 + tgt_y2) // 2)

        # Use seamless cloning for better blending
        try:
            result = cv2.seamlessClone(
                resized_source_face,
                result,
                (mask * 255).astype(np.uint8),
                center,
                cv2.NORMAL_CLONE
            )
        except:
            # Fallback to simple replacement if seamless clone fails
            result[tgt_y1:tgt_y2, tgt_x1:tgt_x2] = resized_source_face

        return result

    def batch_swap(self, source_image_path, target_image_paths, output_dir):
        """
        Swap face onto multiple target images

        Args:
            source_image_path: Path to source face image
            target_image_paths: List of target image paths
            output_dir: Directory to save results

        Returns:
            List of output paths
        """
        output_paths = []

        for i, target_path in enumerate(target_image_paths):
            output_name = f"swapped_{i+1}_{Path(target_path).name}"
            output_path = Path(output_dir) / output_name

            try:
                self.swap_face(source_image_path, target_path, str(output_path))
                output_paths.append(str(output_path))
                print(f"✓ Completed face swap {i+1}/{len(target_image_paths)}")
            except Exception as e:
                print(f"✗ Failed to swap face on {target_path}: {e}")

        return output_paths
