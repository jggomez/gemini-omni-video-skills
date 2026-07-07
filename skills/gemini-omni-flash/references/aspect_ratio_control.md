# Reference: Aspect Ratio Control (Portrait / Landscape)

This reference manual maps the structural parameters required to define and alter frame boundaries for video outputs using the Gemini Omni Flash (`gemini-omni-flash-preview`) model within the Interactions API.

## Core Properties matrix

All dimension controls must be explicitly declared inside the `response_format` configuration block. Leaving this block empty will cause the execution pipeline to fall back to native widescreen standards.

| Key | Type | Supported Values | Default Value | Operational Scope |
| :--- | :--- | :--- | :--- | :--- |
| `aspect_ratio` | String | `"16:9"`, `"9:16"` | `"16:9"` | Dictates the macro pixel orientation layout. |

---

## SDK & REST Syntax Blueprints

### 1. Vertical Framing / Portrait Deployment ("9:16")
Ideal for smartphone screens, mobile advertising, and specialized social media video generation.

#### Python SDK Implementation
```python
import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-omni-flash-preview",
    input="A futuristic city with neon lights and flying cars, cyberpunk style.",
    response_format={
        "type": "video",
        "aspect_ratio": "9:16"  # Activates vertical framing
    }
)

with open("example_vertical.mp4", "wb") as f:
    f.write(base64.b64decode(interaction.output_video.data))
```