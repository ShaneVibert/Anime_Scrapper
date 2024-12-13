# === utils.py ===
import requests  # Add this line
from io import BytesIO
from PIL import Image

def load_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((100, 150), Image.Resampling.LANCZOS)
            return img
    except requests.RequestException as e:
        print(f"Error loading image: {e}")
    return None

