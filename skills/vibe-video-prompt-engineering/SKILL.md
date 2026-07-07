---
name: vibe-video-prompt-engineering
description: Skill for Gemini Omni Flash (gemini-omni-flash-preview) video prompt engineering best practices. Use when the prompt_architect agent needs to structure or refine a video generation prompt, apply the 6-dimension framework, or enforce preservation guardrails on edit turns. Activates when user requests involve video generation, editing, style changes, or camera adjustments.
version: 1.1.0
author: vibe-video-studio
category: prompt-engineering
tags: [gemini-omni-flash, prompt-engineering, video-prompting, edit-turns, best-practices]
---

# Gemini Omni Prompt Engineering Skill

## The 6-Dimension Multimodal Prompt Framework

Structure EVERY video generation prompt using these 6 dimensions embedded naturally in prose:

### 1. Shot Framing & Motion
Explicit camera perspectives and velocity descriptors.
*   **Single Scene Enforcements:**
    - `"In a single unbroken scene"`, `"In a single continuous shot"`, `"No scene cuts"`
*   **Approved patterns:**
    - `"film camera"`, `"natural smartphone zoom"`, `"close-up on [subject]"`
    - `"over-the-shoulder"`, `"bird's eye view"`, `"worm's eye angle"`
    - `"dolly zoom"`, `"push in slowly"`, `"static locked-off"`
    - `"handheld with natural shake"`, `"glide gently"`, `"rush suddenly"`

### 2. Style Aesthetics
Explicit rendering medium and artistic style.
*   **Approved patterns:**
    - `"claymation with rough surface texture"`
    - `"anime with bold outlines and flat color fills"`
    - `"watercolour with bleeding edges and granulated paper texture"`
    - `"3D hyper-realistic with subsurface scattering"`
    - `"risograph print with grainy halftone overlays"`
    - `"contemporary flat-media style with waxy textured strokes"`
    - `"translucent glass material with complex caustics"`

### 3. Lighting & Volumetrics
Illumination origin, physics, and atmospheric effects.
*   **Approved patterns:**
    - `"sunset volumetric golden shafts through forest canopy"`
    - `"off-screen neon glow reflected on wet pavement"`
    - `"internal translucent glow pulsing outward"`
    - `"clinical overhead fluorescent with harsh shadows"`
    - `"light pulses synchronized with audio beats"`
    - `"streetlamps casting long parallel shadows"`

### 4. Location & Environment
Spatial anchor and macro landscape setting.
*   **Approved patterns:**
    - `"minimalist white studio"`, `"dense cyberpunk alleyway at midnight"`
    - `"sparse alien mesa with azure horizon"`, `"brutalist concrete interior"`
    - `"granulated paper background"`, `"dense urban apartment facade at night"`

### 5. Action & Complex Interactions
Explicit subject choreography and physical dynamics.
*   **Approved patterns:**
    - `"skateboarder executes kickflip at peak arc"`
    - `"petals spiral outward in slow-motion burst"`
    - `"character turns to camera and raises both hands"`
    - `"birds loosely form structural letter layout"`

### 6. Text & Typographic Rendering
Typeface, placement, pacing (only when text is in the video).
*   **Approved patterns:**
    - `"one word on the screen at a time: 'did, you, know...?' where each word appears for 1s with a different animated style. No dialogue."`
    - `"there is a street sign that says: 'This is an AI generation by Omni'"`
    - `"storefront that says: 'All you need AI'"`

---

## Negative Prompting Constraints
To eliminate unwanted audio or visual features, use simple negative keywords:
- `"No dialogue"`
- `"No embellishments"`
- `"No extra sound effects"`

---

## Audio Prompting
Explicitly direct audio styles and music:
- `"Include calm background music"`
- `"The video has a high energy techno beat"`
- `"The audio is a low tinny radio broadcast in the background, playing a song"`

---

## Event Timing Syntax
You can specify exact durations for events:
*   **Natural syntax:**
    - `"After 3 seconds, a woman enters the scene."`
    - `"At 5s the chorus starts in the background audio."`
    - `"Every 2s cut to a new frame."`
    - `"In a rapid fire sequence, every half a second (12 frames at 24fps) change the scene to a new location."`
*   **Timecode syntax:**
    - `[0-3s] A person is walking`
    - `[3-6s] They stop and turn around`
    - `[6-10s] They start running`

---

## Multimodal Tag Rules
Set specific roles for uploaded images:
- **Simple Tags:**
  - `<FIRST_FRAME>`: Starting frame anchor. (e.g. `<FIRST_FRAME> a woman is walking`)
  - `<IMAGE_REF_N>`: Reference style/character starting from 0. (e.g. `in the style of <IMAGE_REF_0> a woman is walking`)
- **Explicit Declarations:**
  - `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] a woman <IMAGE_REF_0> is walking. Use Image1 as the starting frame. Use Image2 as a reference for the video generation.`

---

## Edit Turn Preservation Guardrails (CRITICAL)

When editing an existing video (turn >= 2), ALWAYS:

1. **Start with the preservation phrase**: `"Edit this keeping everything else identical."`
2. **Simplify the edits**: Avoid long descriptions of physics; isolate only the swap.
3. **Examples:**
   - *Avoid:* "In the video of the man sitting on the sofa, please add a small black cat that runs from the right..."
   - *Simplify:* `"Add a cat that jumps onto his lap, he begins to pet it. Keep everything else the same."`
   - *Avoid:* "Please remove the cell phone that the person is holding..."
   - *Simplify:* `"Make the phone invisible. Keep everything else the same."`

---

## Anti-patterns & Limitations (Never Use)

| Anti-pattern / Limitation | Why | Alternative / Mitigation |
|---|---|---|
| "make it cool" | Abstract, unstructured | Define exact style + lighting |
| "animate it" | No kinetic spec | Describe exact motion vector |
| "better quality" | Subjective | Define rendering style explicitly |
| Long adjective stacks | Over-specifies what model handles | Trust model's world knowledge |
| Describing physics | Model handles naturally | Focus on macro intent |
| Uploading audio references | Unsupported by API | Describe audio/music in text prompt |
| Multiple video references | Unsupported by API | Prompt using only one video reference |
| Video extension / interpolation | Unsupported by API | Render a complete new generation |
| YouTube URL inputs | Unsupported by API | Download and upload file via Files API (if allowed) |
| Minors/recognizable people in inputs | Blocked by safety filter | Use generic representations |
| Uploading custom videos (EEA/UK/CH) | Editing uploaded files blocked | Only use on generated videos (supported) |

---

## 4-Turn Drift Threshold

After the 4th consecutive edit turn, visual consistency decays exponentially:
- Character identity drift
- Texture and detail inconsistency
- Background element mutations

**Mitigation**: Warn user at turn 3. Recommend starting fresh at turn 4+.

