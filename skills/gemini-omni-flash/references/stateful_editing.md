# Reference: Multi-Turn Chaining & Stateful Video Editing

This reference manual documents the state tracking mechanisms, parameter injections, and implementation workflows required to perform iterative, multi-turn video editing using the Gemini Omni Flash (`gemini-omni-flash-preview`) model via the Interactions API.

## 1. Interaction Chaining Mechanics

Unlike traditional video generation models that require rendering a completely new asset from scratch upon every prompt variation, Gemini Omni Flash natively tracks session history within the Interactions cluster. 

```
[Initial Prompt] ---> client.interactions.create() ---> Returns ID: "v1_gen_alpha"
|
v
[Edit Prompt]    ---> client.interactions.create(
                           previous_interaction_id="v1_gen_alpha"
                      )                           ---> Returns ID: "v1_edit_beta"
```

Every execution cycle yields a unique `interaction_id`. To apply incremental mutations to that specific output sequence, the developer must feed that exact token string into the subsequent request payload using the `previous_interaction_id` field.

---

## 2. Structural SDK Implementation Blueprints

### A. Two-Turn Modification Sequence (Python SDK)
This blueprint initializes a baseline generative layout, isolates its tracking identifier, and applies a localized environmental mutation over the context pipeline. Explicitly configure the task as `"edit"` for turn 2.

```python
import base64
from google import genai

client = genai.Client()

# Turn 1: Primary Asset Initialization
initial_turn = client.interactions.create(
    model="gemini-omni-flash-preview",
    input="A golden retriever dog running across an open grassy park.",
    response_format={
        "type": "video",
        "aspect_ratio": "16:9"
    }
)

captured_token = initial_turn.id
print(f"Turn 1 completed successfully. Session Anchor: {captured_token}")

# Turn 2: Stateful Edit Sequence referencing the captured Anchor
edited_turn = client.interactions.create(
    model="gemini-omni-flash-preview",
    previous_interaction_id=captured_token,
    input="Edit this keeping everything else identical. Change the setting to a snowy winter wonderland.",
    generation_config={
        "video_config": {
            "task": "edit"
        }
    }
)

# Extract and decode Base64 output video data
with open("final_stateful_output.mp4", "wb") as f:
    f.write(base64.b64decode(edited_turn.output_video.data))
```

### B. Infinite Generative Evolution (JavaScript SDK)

Demonstrates multi-turn dependency nesting by continuously shifting down the conversation tracking timeline.

```javascript
import { GoogleGenAI } from '@google/genai';
import * as fs from 'fs';
const ai = new GoogleGenAI();

// Turn 1: Base Generation
const turn1 = await ai.interactions.create({
  model: 'gemini-omni-flash-preview',
  input: 'A single butterfly resting on a flower.'
});

// Turn 2: First Contextual State Shift (Butterfly -> Bee)
const turn2 = await ai.interactions.create({
  model: 'gemini-omni-flash-preview',
  previous_interaction_id: turn1.id,
  input: 'Edit this keeping everything the same. Change the butterfly to a bee.',
  generationConfig: {
    videoConfig: {
       task: 'edit'
    }
  }
});

// Turn 3: Second Contextual State Shift (Bee -> Swarm of Fireflies)
const turn3 = await ai.interactions.create({
  model: 'gemini-omni-flash-preview',
  previous_interaction_id: turn2.id,
  input: 'Edit this keeping everything the same. Change the bee into a small swarm of fireflies.',
  generationConfig: {
    videoConfig: {
       task: 'edit'
    }
  }
});

if (turn3.output_video?.data) {
  fs.writeFileSync('output_evolution.mp4', Buffer.from(turn3.output_video.data, 'base64'));
}
```

### C. Edit Your Own Uploaded Videos (Files API)

You can upload your own custom video using the Files API and then edit it with Gemini Omni Flash.

```python
import time
import base64
from google import genai

client = genai.Client()

# 1. Upload video using the Files API
video_file = client.files.upload(file="Video.mp4")

# 2. Poll until file processing is complete
while video_file.state == "PROCESSING":
    print("Waiting for video to be processed...")
    time.sleep(10)
    video_file = client.files.get(name=video_file.name)

if video_file.state == "FAILED":
    raise ValueError("Video processing failed.")
print(f"Video processing complete: {video_file.uri}")

# 3. Create interaction to edit the uploaded video
interaction = client.interactions.create(
    model="gemini-omni-flash-preview",
    input=[
        {"type": "document", "uri": video_file.uri},
        {"type": "text", "text": "When the person touches the mirror, make the mirror ripple beautifully like liquid, and the person's arm turns into reflective mirror material"}
    ],
    generation_config={
        "video_config": {
            "task": "edit"
        }
    }
)

with open("edited_uploaded_video.mp4", "wb") as f:
    f.write(base64.b64decode(interaction.output_video.data))
```

### D. Raw Wire Protocol / HTTP REST Query

When querying the raw API directly, map the state anchor value at the root level of the JSON payload. Note that the convenience field `interaction.output_video` is SDK-only; in REST, extract the base64 data from the `steps` array.

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions?key=$API_KEY" \
-H "Content-Type: application/json" \
-d '{
 "model": "gemini-omni-flash-preview",
 "previous_interaction_id": "v1_insert_previous_interaction_token_here",
 "input": "Change the camera angle to be over the violinist shoulder.",
 "generation_config": {
   "video_config": {
     "task": "edit"
   }
 }
}'
```

---

## 3. High-Performance Prompts & Control Phrases

To minimize prompt drift and preserve background structures across complex multi-turn updates, you must inject deterministic control anchors into the `input` descriptions:

* **Preservational Key:** Force the instruction to inherit clauses such as `"Edit this keeping everything else identical"` or `"keeping everything the same"`.
* **Targeted Isolation:** Explicitly specify what asset is being modified or removed, and let the model's world knowledge handle physics transitions natively (e.g., changing background seasons, moving camera angles to over-the-shoulder, or syncing structural animations like apartment lights to audio tracks).

---

## 4. Operational Guardrails & Limitations

* **The 4-Turn Drift Threshold:** Multi-turn chaining quality begins to degrade exponentially after the **4th consecutive modification turn**. Minor details, character consistency, and high-frequency textures will experience structural drift. Warn developers at Turn 3 and recommend starting fresh beyond Turn 4.
* **Asynchronous Processing Conflicts:** Setting `"background": true` within the execution payload causes known race condition failures inside stateful chained edits. For stateful multi-turn consistency, explicitly enforce synchronous unary execution (`background=false`, `store=false`, `stream=false`).
* **EEA Regional & Safety Restrictions:** 
  * Uploading/editing videos containing **minors** or **recognizable celebrity/children likenesses** is strictly blocked.
  * For users in the European Economic Area (EEA), Switzerland, and the United Kingdom, **editing custom uploaded videos is not supported** (only editing videos generated by the model itself is allowed).
* **API Restrictions & Deprecations:**
  * **Audio Ingestion:** Uploading custom audio references is completely unsupported.
  * **Video Durations:** Video references under 3 seconds are accepted by the API schema but are not correctly processed by the model.
  * **Multi-Video Prompting:** Referencing or reasoning across multiple videos is unsupported.
  * **Voice Editing:** Voice-based editing is not supported.
  * **Deprecated Params:** Native parameters like `system_instructions`, `temperature`, `top_p`, and negative prompt matrices are unsupported. Negatives must be handled in prose (e.g. *"Do not do X"*).
  * **Video Extensions:** Video interpolation (generating a video between start and end frames) or extension is unsupported.
  * **YouTube Sources:** Using YouTube URLs as input is unsupported.
* **SynthID Watermarking:** Every generated or edited video contains an un-removable, invisible SynthID watermarking payload for provenance verification.