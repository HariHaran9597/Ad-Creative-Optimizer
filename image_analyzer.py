import cv2
import numpy as np
import os
import json

def analyze_image(image_path):
    """Analyze a single image"""
    img = cv2.imread(image_path)
    if img is None:
        return {"error": f"Image {image_path} not found"}
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Text coverage calculation
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    text_coverage = cv2.countNonZero(thresh) / (img.shape[0] * img.shape[1])
    
    # Brightness and contrast
    brightness = np.mean(gray)
    contrast = np.std(gray)
    
    return {
        "image": os.path.basename(image_path),
        "text_coverage": round(text_coverage, 4),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2)
    }

def analyze_all_images(folder="data"):
    """Analyze all images in a folder"""
    results = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder, filename)
            results.append(analyze_image(image_path))
    return results

if __name__ == "__main__":
    print(json.dumps(analyze_all_images(), indent=2))