import base64
from openai import OpenAI
import os
from scripts.utils import ensure

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OUT_DIR = "public/assets/img/"

def generate_image(prompt, filename):
    ensure(OUT_DIR)
    result = client.images.generate(
        model="gpt-image-1-mini",
        prompt=prompt,
        size="1024x1024"
    )
    img_data = result.data[0].b64_json
    path = OUT_DIR + filename
    with open(path, "wb") as f:
        f.write(base64.b64decode(img_data))
    return path
