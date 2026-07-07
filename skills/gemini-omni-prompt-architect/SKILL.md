---
name: gemini-omni-prompt-architect
description: Guides development, structured formatting, and iterative refinement of multimodal prompts for the Gemini Omni world model. Use this skill when a user requires composition or modifications of video, text rendering, multi-input syncing, camera direction, or style morphing.
version: 1.1.0
author: gemini-omni-video-skills community
category: prompt-engineering
tags: [gemini-omni, prompt-engineering, video-prompting, editing-turns]
---

# Gemini Omni Prompt Architect

## Procedural Instructions

### 1. Core Mindset Shift: World Knowledge vs. Micromanagement
- Gemini Omni possesses deeply embedded physical reasoning and world understanding.
- **Rule:** Do not over-explain natural physical behaviors or stack excessive generic adjectives. Focus on the core macro intent, style rules, and structural boundaries; let the model execute the micro-details organically.

### 2. Single Scene Framing & Negative Prompting
- By default, Omni Flash attempts to create a video with multiple cuts to craft a narrative.
- To enforce a **single scene** without edits, explicitly use one of these phrases:
  - `"In a single unbroken scene"`
  - `"In a single continuous shot"`
  - `"No scene cuts"`
- To remove unwanted elements or behaviors, use explicit negative constraints:
  - `"No dialogue"`
  - `"No embellishments"`
  - `"No extra sound effects"`

### 3. Primary 6-Dimension Structural Framework
When building a prompt from scratch, coordinate these 6 vectors:
1. **Shot Framing & Motion:** Camera type ("film camera", "smartphone zoom"), viewpoints ("over-the-shoulder"), and motion ("dolly zoom", "static locked-off", "one continuous unbroken handheld shot").
2. **Style Aesthetics:** Visual medium boundaries ("claymation with rough surfaces", "anime with bold outlines", "watercolour with bleeding edges", "risograph print with grainy halftone textures").
3. **Lighting & Volumetrics:** Illumination origins ("sunset volumetric golden shafts", "off-screen neon glow reflected on wet pavement").
4. **Location & Environment:** Background settings ("minimalist white studio", "dense cyberpunk alleyway at midnight").
5. **Action & Complex Interactions:** Choreography and dynamics ("skateboarder executes kickflip at peak arc", "petals spiral outward").
6. **Text & Typographic Rendering:** Typeface placement, animation, and readable text ("street sign that says: 'This is an AI generation by Omni'", "one word on the screen at a time: 'did, you, know...?' where each word appears for 1s with a different animated style. No dialogue.").

### 4. Conversational Editing & Simplify Patterns (CRITICAL for turn >= 2)
- **The Preservational Guardrail:** Keep edit prompts simple. Overly descriptive requests lead to unintended changes. Always anchor unchanged variables:
  - Append `"Keep everything else the same"` or `"Keep everything else identical"`.
- **Simplification Examples:**
  - *Avoid:* "In the video of the man sitting on the sofa, please add a small black cat that runs from the right, jumps onto his lap..."
  - *Use:* `"Add a cat that jumps onto his lap, he begins to pet it. Keep everything else the same."`
  - *Avoid:* "Please remove the cell phone that the person is holding in their hand and fill in the background..."
  - *Use:* `"Make the phone invisible. Keep everything else the same."`

### 5. Audio Prompting
Describe the custom soundtrack and mood explicitly, especially if music is desired:
- `"Include calm background music"`
- `"The video has a high energy techno beat"`
- `"The audio is a low tinny radio broadcast in the background, playing a song"`

### 6. Timing Events (Natural and Timecode Syntax)
You can direct events to trigger at exact durations:
- **Natural syntax:**
  - `"After 3 seconds, a woman enters the scene."`
  - `"At 5s the chorus starts in the background audio."`
  - `"Every 2s cut to a new frame."`
  - `"In a rapid fire sequence, every half a second (12 frames at 24fps) change the scene to a new location."`
- **Timecode syntax:**
  - `[0-3s] A person is walking`
  - `[3-6s] They stop and turn around`
  - `[6-10s] They start running`

### 7. Meta Prompting
Direct general quality standards for complex scenes:
- `"Consider micro-detail, expression and timing to create a very rich, detailed but entirely natural scene."`
- `"Be extremely detailed in your descriptions of characters and environments. Apply costume design principles to characters."`
- `"Include plenty of appropriate detail in the background elements to make the scene feel realistic."`

### 8. Multimodal Tags for Image Roles
When handling uploaded images, use tags to declare their roles:
1. **Simple Tags (Recommended):**
   - `<FIRST_FRAME>`: Anchor image as starting frame. (e.g. `<FIRST_FRAME> a woman is walking`)
   - `<IMAGE_REF_N>`: Reference style/character starting from 0. (e.g. `in the style of <IMAGE_REF_0> a woman is walking`)
2. **Explicit Declarations:**
   - Format: `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] a woman <IMAGE_REF_0> is walking.`
   - Guiding instruction suffix: Use `"Use Image1 as the starting frame."` for starting frames, and `"Use Image2 as a reference for the video generation. The images should not be used as literal initial frames."` for reference images.

---

## Technical Constraints & Guardrails
- **The 4-Turn Drift Threshold:** Consistency decays after Turn 4. Warn developers at Turn 3.
- **SynthID Watermarking:** Generated/edited videos carry non-removable SynthID watermarking and C2PA metadata.

---

## Structural Examples

### Example 1: Image-to-Video Anchor with Style Reference
```text
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]
A continuous, unbroken handheld shot of a woman walking down a busy street in the style of <IMAGE_REF_0>. Use Image1 as the starting frame. Use Image2 as a reference for video generation. Keep everything else the same. No dialogue.
```