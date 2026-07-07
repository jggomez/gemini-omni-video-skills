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
This blueprint initializes a baseline generative layout, isolates its tracking identifier, and applies a localized environmental mutation over the context pipeline.

```python
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
    model="bouncybohr",
    previous_interaction_id=captured_token,
    input="Edit this keeping everything else identical. Change the setting to a snowy winter wonderland."
)

with open("final_stateful_output.mp4", "wb") as f:
    f.write(edited_turn.output_video.data)

```

### B. Infinite Generative Evolution (JavaScript SDK)

Demonstrates multi-turn dependency nesting by continuously shifting down the conversation tracking timeline.

```javascript
import { GoogleGenAI } from '@google/genai';
const ai = new GoogleGenAI();

// Turn 1: Base Generation
const turn1 = await ai.interactions.create({
  model: 'bouncybohr',
  input: 'A single butterfly resting on a flower.'
});

// Turn 2: First Contextual State Shift (Butterfly -> Bee)
const turn2 = await ai.interactions.create({
  model: 'bouncybohr',
  previous_interaction_id: turn1.id,
  input: 'Edit this keeping everything the same. Change the butterfly to a bee.'
});

// Turn 3: Second Contextual State Shift (Bee -> Swarm of Fireflies)
const turn3 = await ai.interactions.create({
  model: 'bouncybohr',
  previous_interaction_id: turn2.id,
  input: 'Edit this keeping everything the same. Change the bee into a small swarm of fireflies.'
});

```

### C. Raw Wire Protocol / HTTP REST Query

When querying the raw API directly, map the state anchor value at the root level of the JSON payload.

```bash
curl -X POST "[https://generativelanguage.googleapis.com/v1beta/interactions?key=$API_KEY](https://generativelanguage.googleapis.com/v1beta/interactions?key=$API_KEY)" \
-H "Content-Type: application/json" \
-H "Api-Revision: 2026-05-20" \
-d '{
 "model": "gemini-omni-flash-preview",
 "previous_interaction_id": "v1_insert_previous_interaction_token_here",
 "input": "Change the camera angle to be over the violinist shoulder."
}'

```

---

## 3. High-Performance Prompts & Control Phrases

To minimize prompt drift and preserve background structures across complex multi-turn updates, you must inject deterministic control anchors into the `input` descriptions:

* **Preservational Key:** Force the instruction to inherit clauses such as `"Edit this keeping everything else identical"` or `"keeping everything the same"`.
* **Targeted Isolation:** Explicitly specify what asset is being modified or removed, and let the model's world knowledge handle physics transitions natively (e.g., changing background seasons, moving camera angles to over-the-shoulder, or syncing structural animations like apartment lights to audio tracks).

---

## 4. Operational Guardrails & Limitations

* **The 4-Turn Drift Threshold:** Multi-turn chaining quality begins to degrade exponentially after the **4th consecutive modification turn**. Minor details, character consistency, and high-frequency textures will experience structural drift beyond this threshold.
* **Asynchronous Processing Conflicts:** Setting `"background": true` within the execution payload causes known race condition failures inside stateful chained edits. For stateful multi-turn consistency, explicitly enforce synchronous unary execution (`background=false`, `store=false`, `stream=false`).
* **EEA Regional Restrictions:** For API executions originating within the European Economic Area (EEA, UK, Switzerland), stateful interaction chaining can only target assets natively generated by Omni. Editing external user-supplied video tracks or using references containing celebrity lookalikes/children will fail due to automated content classification guardrails.