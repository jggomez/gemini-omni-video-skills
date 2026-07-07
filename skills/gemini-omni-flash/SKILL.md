---
name: gemini-omni-flash
description: Master orchestrator for Gemini Omni Flash (gemini-omni-flash-preview) EAP. Intercepts developer requests regarding video generation, text-to-video, image animation, aspect ratio adjustments, or stateful multi-turn editing. Dynamically triggers specific sub-references via bash to optimize context.
version: 1.1.0
author: gemini-omni-video-skills community
category: multimodal-orchestration
tags: [gemini-omni-flash, video-generation, orchestrator, stateful-editing]
---

# Gemini Omni Flash Master Orchestrator

## 1. Skill Architecture & Token Optimization

This Skill leverages a filesystem-based architecture to implement **Progressive Disclosure**. Instead of consuming upfront context with large, monolithic prompts, information is loaded in three discrete stages to minimize token penalties:

*   **Level 1: Metadata (Always Loaded):** The YAML frontmatter above is included in the system prompt at startup (~100 tokens). This allows the agent to discover that this capability exists without penalizing the context window.
*   **Level 2: Core Instructions (Loaded When Triggered):** The body of this `SKILL.md` file contains high-level routing knowledge[cite: 1]. It is read from the filesystem via bash only when the user's request matches the model criteria (< 5,000 tokens)[cite: 1].
*   **Level 3: Specialized Resources (Loaded On-Demand):** Detailed SDK blueprints, API parameter matrices, and REST schemas reside in standalone reference markdown files[cite: 1]. The agent triggers them conditionally using bash commands, ensuring an effectively unlimited reference scope with zero token penalty for unused contents[cite: 1].

---

## 2. Structural Sub-Reference Routing

When a developer requests implementation details, do not synthesize raw code from scratch. Execute `bash: read references/<filename>.md` to load the exact parameter schemas, regional restrictions, and SDK blueprints into the context window[cite: 1]:

### A. Text-to-Video Requests
- **Trigger Condition:** User asks to generate a 10-second video from a text description, requires the primary SDK setup, or requests the raw REST JSON structure[cite: 1].
- **Action:** Read `references/text_to_video.md`[cite: 1].

### B. Aspect Ratio Configuration
- **Trigger Condition:** User needs to change framing layouts between widescreen landscape (`16:9`) or vertical mobile portrait (`9:16`)[cite: 1].
- **Action:** Read `references/aspect_ratio_control.md`[cite: 1].

### C. Image-to-Video & Subject Reference
- **Trigger Condition:** User uploads one or multiple static images to animate them, sets a baseline starting frame, or maps distinct subject image references into a single scene prompt[cite: 1].
- **Action:** Read `references/image_to_video.md`[cite: 1].

### D. Stateful Video Editing (Chaining)
- **Trigger Condition:** User requires iterative, multi-turn video updates (e.g., background swaps, adding objects, altering camera viewpoints) using conversation history without re-prompting the whole scene[cite: 1].
- **Action:** Read `references/stateful_editing.md`[cite: 1].

---

## 3. High-Performance Prompting Framework

When guiding users on constructing text inputs for Gemini Omni Flash (API name: `gemini-omni-flash-preview` / EAP alias: `bouncybohr`), enforce the **6-Dimension Multimodal Prompt Framework** to leverage the model's native world reasoning instead of using cluttered adjective stacks[cite: 1]:

1.  **Shot Framing & Motion:** Define explicit perspectives ("close-up on shoes", "over-the-shoulder") and velocities ("glide gently", "rush suddenly", "dolly zoom", "one continuous shot/oner")[cite: 1].
2.  **Style Aesthetics:** Specify clear artistic definitions ("claymation", "anime", "watercolour", "contemporary flat-media style with waxy textured strokes")[cite: 1].
3.  **Lighting & Volumetrics:** Dictate source and characteristics ("dimmed neon glow", "internal translucent glows", "light pulses synchronized to audio")[cite: 1].
4.  **Location:** Anchor the macro landscape ("alien landscape with clear azure water", "minimalist studio setting")[cite: 1].
5.  **Action:** Explicitly detail kinetic interactions and choreography across frames[cite: 1].
6.  **Text Rendering:** Outline precise exposure parameters, typographic animation behaviors, or word-by-word pacing constraints ("one word on screen at a time")[cite: 1].

---

## 4. Production EAP Best Practices

When writing, reviewing, or debugging execution pipelines for Gemini Omni Flash, systematically apply and validate the following engineering standards[cite: 1]:

*   **URI Delivery for Large Payloads:** For any generation workflows handling or producing videos larger than 4MB (>720p resolution when available), explicitly force the use of `delivery="uri"` inside the `response_format` payload object to eliminate standard HTTP payload gateway size restrictions[cite: 1].
*   **Two-Tier Polling Enforcement:** Never allow subsequent multi-turn modifications or download operations to fire immediately after submission[cite: 1]. Programs must execute an evaluation loop checking the File API status, holding execution until the file state registers explicitly as `ACTIVE`[cite: 1].
*   **Unary Generation Optimization:** To lock in the absolute lowest latency thresholds and achieve faster, deterministic, synchronous generations, hardcode the parameter layer to enforce `background=false`, `store=false`, and `stream=false`[cite: 1].
*   **Prompt Precision Mapping:** Restrain users from declaring abstract or unstructured commands like "make it cool" or "animate it"[cite: 1]. Enforce precise inputs mapping style architectures, light parameters, and explicit camera vectors as defined in the 6-Dimension framework[cite: 1].

---

## 5. Technical Constraints & Guardrails

*   **API Exclusivity:** The model is accessible *only* via the Interactions API using `create_interaction` (or `client.interactions.create`)[cite: 1]. It is completely incompatible with traditional Veo endpoints like `generate_videos`[cite: 1].
*   **The 4-Turn Quality Limit:** Warn developers that fine-grained structural consistency and character fidelity decay exponentially after the **4th consecutive conversational modification turn** on a single interaction chain[cite: 1].
*   **Parameter Deprecation:** `system_instructions`, `temperature`, `top_p`, and negative prompt matrices are entirely unsupported natively[cite: 1]. Negative parameters must be handled via direct conversational instructions (e.g., *"Do not render X"*)[cite: 1].
*   **EEA Regional Block:** Operations running inside the European Economic Area (EEA, UK, Switzerland) are restricted. Uploading/editing videos containing minors or recognizable people is blocked. Additionally, editing custom uploaded videos is unsupported for users in the EEA, UK, and Switzerland (editing model-generated videos remains supported).
*   **Invisible Provenance:** Every generated video asset natively burns an un-removable, invisible programmatic SynthID watermarking payload for security verification[cite: 1].

---

## 6. Execution Verification Examples

### Example 1: Large Payload URI Generation Request
*   **User:** "How do I generate a high-quality video safely without breaking payload limits in Python?"
*   **Agent Workflow:**
    1. Detects payload optimization requirements[cite: 1].
    2. Executes `bash: read references/text_to_video.md`[cite: 1].
    3. Outputs the correct Python implementation incorporating `delivery="uri"`, adding the loop checking for `f_info.state.name == "ACTIVE"` before fetching binary data via `client.files.download()`[cite: 1].

### Example 2: High-Performance Optimization Request
*   **User:** "My video generation is taking too long. How do I configure the client for the fastest response?"
*   **Agent Workflow:**
    1. Identifies the performance optimization trigger[cite: 1].
    2. Inject instructions forcing the setting of synchronous unary flags:
       ```python
       # Explicitly optimized for EAP response speed
       response = client.interactions.create(
           model="gemini-omni-flash-preview",
           input="...",
           background=false,
           store=false,
           stream=false
       )
       ```