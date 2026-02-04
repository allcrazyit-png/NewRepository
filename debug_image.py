import os
from PIL import Image

img_path = "quality_images/76901_2-BZ200_190_main.jpg"

print(f"Checking: {img_path}")
if os.path.exists(img_path):
    print(f"File exists. Size: {os.path.getsize(img_path)} bytes")
    try:
        img = Image.open(img_path)
        print(f"Image opened successfully. Format: {img.format}, Size: {img.size}")
    except Exception as e:
        print(f"FAILED to open image: {e}")
else:
    print("File does NOT exist.")
