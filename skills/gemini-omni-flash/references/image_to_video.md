# Reference: Image-to-Video & Subject Reference Execution

This reference manual documents the ingestion patterns and execution parameters required to animate static images or apply specific subject identities using the Gemini Omni Flash (`gemini-omni-flash-preview`) model.

## Operational Modalities

The model handles image inputs under two distinct behavioral paradigms depending on the array structure and text intent:

1. **Image-to-Video (Animation):** Animates a unique baseline image (often specified as the starting frame) using an accompanying prompt that describes the camera velocity, subject motion, or environmental progression.
2. **Subject Reference:** Uses one or multiple images as structural or character anchors to compose a dynamic scene described in the text input (e.g., matching a reference cat with a reference object).

---

## SDK & REST Implementation Blueprints

### 1. Standard Image Animation (Image-to-Video)
Animates a single source image. For optimal quality, avoid vague text inputs like "make it move"; enforce precise descriptors of camera behavior or environmental physics. Explicitly configure the task as `"image_to_video"`.

#### Python SDK Implementation
```python
import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-omni-flash-preview",
    input=[
        {"type": "image", "data": base64_image_data, "mime_type": "image/jpeg"},
        {"type": "text", "text": "turn this into realistic footage, using the drawing only as a guide for movement, do not show the drawing in the final video"}
    ],
    generation_config={
        "video_config": {
            "task": "image_to_video"
        }
    }
)

# Extract and decode Base64 video data
with open("clownfish.mp4", "wb") as f:
    f.write(base64.b64decode(interaction.output_video.data))
```

### 2. Subject Reference
Generates a video incorporating specific subjects provided as multiple reference images (e.g., a cat and yarn). Use the task `"reference_to_video"` to guide the model.

#### Python SDK Implementation
```python
import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-omni-flash-preview",
    input=[
        {"type": "image", "data": cat_b64, "mime_type": "image/png"},
        {"type": "image", "data": yarn_b64, "mime_type": "image/png"},
        {"type": "text", "text": "A cat playfully batting at a ball of yarn."}
    ],
    generation_config={
        "video_config": {
            "task": "reference_to_video"
        }
    }
)

# Extract and decode Base64 video data
with open("cat_playing.mp4", "wb") as f:
    f.write(base64.b64decode(interaction.output_video.data))
```