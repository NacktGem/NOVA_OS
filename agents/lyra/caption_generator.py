

# agents/lyra/caption_generator.py

import os
from typing import Optional
from PIL import Image, UnidentifiedImageError
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

class CaptionGenerator:
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", use_gpu: Optional[bool] = True):
        self.device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)

    def generate_caption(self, image_path: str, max_length: int = 50) -> str:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            image = Image.open(image_path).convert("RGB")
        except UnidentifiedImageError as e:
            raise ValueError(f"Invalid image file: {image_path}") from e

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        output = self.model.generate(**inputs, max_new_tokens=max_length)
        caption = self.processor.decode(output[0], skip_special_tokens=True)
        return caption

# Example usage (for testing only)
# if __name__ == "__main__":
#     generator = CaptionGenerator()
#     print(generator.generate_caption("sample.jpg"))