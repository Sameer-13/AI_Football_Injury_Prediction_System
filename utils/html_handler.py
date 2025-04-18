import base64
from io import BytesIO

def logo_to_base64(img):
    """Convert a PIL image to base64 string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()