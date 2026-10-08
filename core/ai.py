"""
The AI part of CivicLens.

We use CLIP, a free pre-trained AI model from OpenAI. CLIP can compare a photo with
sentences like "a photo of a pothole on a road" and tell which sentence matches best.
This is called ZERO-SHOT classification: it works WITHOUT you collecting and training
on your own dataset. (Later, you can train your own model to make it more accurate.)

The first time it runs, the model (~600 MB) downloads automatically from the internet.
"""
import io
from pathlib import Path

import streamlit as st
from PIL import Image

import config

MODEL_NAME = "openai/clip-vit-base-patch32"
# The model is saved INSIDE the project (civiclens/models/clip), so after the first
# download the app works offline too - handy at the expo.
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "clip"
MODEL_FILES = ["*.json", "*.txt", "pytorch_model.bin"]


@st.cache_resource(show_spinner="Loading the AI model (first time downloads ~600 MB)...")
def _load_model():
    """Load the model once and keep it in memory. (If loading fails, nothing is cached,
    so the app simply tries again on the next photo.)"""
    from transformers import CLIPModel, CLIPProcessor
    if not (MODEL_DIR / "pytorch_model.bin").exists():
        from huggingface_hub import snapshot_download
        snapshot_download(MODEL_NAME, local_dir=str(MODEL_DIR), allow_patterns=MODEL_FILES)
    model = CLIPModel.from_pretrained(str(MODEL_DIR))
    processor = CLIPProcessor.from_pretrained(str(MODEL_DIR))
    model.eval()
    return model, processor


def load_model():
    """Returns (model, processor), or None if it can't load (the reason is shown on screen)."""
    try:
        return _load_model()
    except Exception as e:  # no internet, library missing, broken download, etc.
        print("\n*** AI model could not be loaded:", repr(e), "\n")
        st.session_state["ai_error"] = repr(e)
        return None


def classify(image_bytes):
    """
    Look at a photo and guess the problem category.
    Returns (category, confidence 0-1, all_scores) or (None, 0, {}) if the AI is unavailable.
    """
    loaded = load_model()
    if loaded is None:
        return None, 0.0, {}
    model, processor = loaded

    import torch

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    categories = list(config.AI_PROMPTS.keys())
    sentences = list(config.AI_PROMPTS.values())

    inputs = processor(text=sentences, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits_per_image          # how well the photo matches each sentence
    probs = logits.softmax(dim=1)[0].tolist()              # turn into percentages that add up to 100%

    scores = dict(zip(categories, probs))
    best = max(scores, key=scores.get)
    return best, scores[best], scores
