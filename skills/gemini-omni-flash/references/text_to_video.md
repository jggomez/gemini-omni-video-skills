# Reference: Text-to-Video Generation with Gemini Omni Flash

This reference manual provides technical execution patterns for initiating 10-second video generations from text instructions using the `gemini-omni-flash-preview` model via the Interactions API.

## Core Parameter Specification

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `model` | String | **Yes** | Must strictly be set to `"gemini-omni-flash-preview"`. |
| `input` | String | **Yes** | Detailed natural language prompt mapping the layout, motion, and aesthetics. |
| `response_format` | Object | No | Configuration settings for asset structure and payload transit. |
| `response_format.type` | String | No | Must be set to `"video"`. |
| `response_format.aspect_ratio` | String | No | Defines frame boundaries. Supported values: `"16:9"` (default landscape) or `"9:16"` (portrait). |
| `response_format.delivery` | String | No | Use `"uri"` for large payloads (>4MB) to route via Cloud File storage. |

---

## SDK & REST Implementation Blueprints

### 1. Python SDK Implementation
Standard synchronous deployment delivering binary payload data.

```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="bouncybohr",
    input="A hyper-realistic close-up of a cat drinking a large cup of tea.",
    response_format={
        "type": "video",
        "aspect_ratio": "16:9"
    }
)

# Extract binary data directly from convenience field
with open("output_cat.mp4", "wb") as f:
    f.write(interaction.output_video.data)
```