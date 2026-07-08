# Gemini Omni Video Skills

A production-ready library of agent skills designed to orchestrate video generation, structured prompting, and stateful video editing with Gemini Omni Flash (`gemini-omni-flash-preview`).

These skills are optimized for **Progressive Disclosure** to keep token usage low while giving LLM agents full access to advanced generation patterns, parameters, and workflows.

[![Validate Skills](https://github.com/jggomez/gemini-omni-video-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/jggomez/gemini-omni-video-skills/actions/workflows/validate-skills.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📂 Repository Structure

The repository organizes skills in the `skills/` directory, keeping the root folder clean:

```text
gemini-omni-video-skills/
├── .github/
│   ├── ISSUE_TEMPLATE/       # Templates for bug reports and new skill proposals
│   └── workflows/
│       └── validate-skills.yml  # CI workflow to auto-verify skill format and references
├── skills/
│   ├── gemini-omni-flash/              # Master orchestrator for Gemini Omni Flash
│   │   ├── SKILL.md
│   │   └── references/                 # Level 3 references loaded on demand
│   │       ├── aspect_ratio_control.md
│   │       ├── image_to_video.md
│   │       ├── stateful_editing.md
│   │       └── text_to_video.md
│   ├── gemini-omni-prompt-architect/   # Formats and refines video prompts
│   │   └── SKILL.md
│   └── vibe-video-prompt-engineering/  # Best practices, anti-patterns, and edit turn constraints
│       └── SKILL.md
├── scripts/
│   └── validate.py           # Local validation script to verify skill structure
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ Available Skills

### 1. [gemini-omni-flash](file:///Users/jggomez/Documents/jggomez/code/gemini-omni-video-skills/skills/gemini-omni-flash/SKILL.md)
*   **Purpose:** Master orchestrator for Gemini Omni Flash.
*   **Scope:** Detects user intents (text-to-video, image animation, aspect ratio changes, multi-turn stateful edits) and routes the agent to specialized, contextual references located in `skills/gemini-omni-flash/references/`.
*   **Key Feature:** Uses Level-3 on-demand references to save context window tokens.

### 2. [gemini-omni-prompt-architect](file:///Users/jggomez/Documents/jggomez/code/gemini-omni-video-skills/skills/gemini-omni-prompt-architect/SKILL.md)
*   **Purpose:** Procedural builder for constructing rich, high-fidelity prompts for Gemini Omni.
*   **Scope:** Implements the 6-dimension prompt framework, timing event syntaxes, negative constraints, audio descriptions, and multimodal image reference tag mappings (`<FIRST_FRAME>`, `<IMAGE_REF_N>`).

### 3. [vibe-video-prompt-engineering](file:///Users/jggomez/Documents/jggomez/code/gemini-omni-video-skills/skills/vibe-video-prompt-engineering/SKILL.md)
*   **Purpose:** Deep guidance on prompt optimization, limits, and preservation.
*   **Scope:** Details visual anti-patterns, drift thresholds (consistency decay after Turn 4), and critical preservation guardrails for multi-turn edit loops.

---

## 🚀 How to Use These Skills in Your Agent Workspace

To make these skills discoverable by other AI agents (such as Google Antigravity, Claude Code, etc.), choose one of the following integration paths:

### Option A: Install via `npx skills` (Recommended for Claude Code & Vercel Skills CLI)
You can install individual skills directly from this GitHub repository using the `npx skills` package manager:
```bash
# Install the Gemini Omni Flash master orchestrator
npx skills add jggomez/gemini-omni-video-skills/skills/gemini-omni-flash

# Install the Prompt Architect skill
npx skills add jggomez/gemini-omni-video-skills/skills/gemini-omni-prompt-architect

# Install the Vibe Video Prompt Engineering skill
npx skills add jggomez/gemini-omni-video-skills/skills/vibe-video-prompt-engineering
```

To run a skill temporarily in your active agent session without permanent installation, run:
```bash
npx skills use jggomez/gemini-omni-video-skills/skills/gemini-omni-flash
```

### Option B: Local Symlinking (Alternative for Development)
Symlink this repository's folders into your agent's local skills directory (typically under `~/.gemini/skills/` or equivalent):
```bash
ln -s "$(pwd)/skills/gemini-omni-flash" ~/.gemini/skills/gemini-omni-flash
ln -s "$(pwd)/skills/gemini-omni-prompt-architect" ~/.gemini/skills/gemini-omni-prompt-architect
ln -s "$(pwd)/skills/vibe-video-prompt-engineering" ~/.gemini/skills/vibe-video-prompt-engineering
```

### Option C: Configuration Declaration
Point your agent runner's config file (e.g. `agent.json`, `config.yaml`, or setup scripts) to include the absolute paths of the skills folders:
```json
{
  "skills_paths": [
    "/absolute/path/to/gemini-omni-video-skills/skills/gemini-omni-flash",
    "/absolute/path/to/gemini-omni-video-skills/skills/gemini-omni-prompt-architect",
    "/absolute/path/to/gemini-omni-video-skills/skills/vibe-video-prompt-engineering"
  ]
}
```

---

## 🔌 Model Context Protocol (MCP) Server

This repository includes a built-in MCP server ([omni_mcp_server.py](file:///Users/jggomez/Documents/jggomez/code/gemini-omni-video-skills/mcp_server/omni_mcp_server.py)) that exposes Gemini Omni video generation and editing capabilities directly as tools to AI coding agents (like Claude Desktop, Cursor, or Claude Code).

### ⚙️ Option 1: Run with `uv` (Recommended - Zero Setup)
The script includes PEP 723 inline dependency metadata. If you have Astral's `uv` installed, you can run the server on-the-fly without cloning or manual pip installs!

#### Direct execution from GitHub (No clone needed):
Configure `claude_desktop_config.json` to execute directly via HTTPS:

```json
{
  "mcpServers": {
    "gemini-omni-video": {
      "command": "uv",
      "args": [
        "run",
        "https://raw.githubusercontent.com/jggomez/gemini-omni-video-skills/main/mcp_server/omni_mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY"
      }
    }
  }
}
```

#### Local execution (From cloned repository):
```bash
uv run mcp_server/omni_mcp_server.py
```

### ⚙️ Option 2: Run with standard Python (Manual Install)
If you prefer standard python:
```bash
pip install google-genai mcp httpx
```

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "gemini-omni-video": {
      "command": "python3",
      "args": [
        "/Users/jggomez/Documents/jggomez/code/gemini-omni-video-skills/mcp_server/omni_mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY"
      }
    }
  }
}
```

### 🧰 Available Tools

*   **`generate_video`**: Generate a new video from a structured 6-dimension prompt using Gemini Omni Flash.
    *   `prompt` (string, required): Detailed prompt describing layout, camera movement, styles, etc.
    *   `aspect_ratio` (string, optional): Frame layout (`"16:9"` or `"9:16"`). Default is `"16:9"`.
    *   `image_path` (string, optional): Absolute path to a local image reference to animate (Image-to-Video).
*   **`edit_video`**: Edit the last generated video using a targeted conversational instruction.
    *   `edit_prompt` (string, required): Targeted change request. The tool automatically prefixes it with preservation guardrails.
*   **`get_last_video`**: Get details and the local path of the last generated video in the active session.
*   **`clear_session`**: Clear the session state (resets the interaction chaining token).

The server automatically creates an `gemini_omni_outputs/` directory in your home directory and saves all generated/edited MP4s there.

### 📝 Reusable Prompt Templates (MCP Prompts)

The server exposes 4 parameterized prompt templates that implement Gemini Omni prompt engineering best practices:

*   **`create_omni_prompt`**: Builds a fully optimized 6-dimension prompt.
    *   `action` (string, required): Main subject action or behavior.
    *   `style` (string, required): Visual aesthetic style (e.g. `realistic film`, `claymation`).
    *   `location` (string, required): Environmental setting.
    *   `lighting` (string, required): Lighting attributes.
    *   `motion` (string, required): Camera movement vectors.
    *   `text_overlay` (string, optional): Text layout overlay guidelines.
*   **`edit_omni_prompt`**: Formats edit instructions with mandatory turn preservation prefix.
    *   `edit_instruction` (string, required): Change to apply (e.g. `Make the coat red`).
*   **`rapid_fire_prompt`**: Formats a sequence of scenes shifting locations every 0.5 seconds.
    *   `style` (string, required): Aesthetic theme.
    *   `locations` (string, required): Comma-separated list of locations.
*   **`timecode_prompt`**: Formats a narrative sequence using precise timecodes.
    *   `scene_0_3s` (string, required): Staged action from 0 to 3 seconds.
    *   `scene_3_6s` (string, required): Staged action from 3 to 6 seconds.
    *   `scene_6_10s` (string, required): Staged action from 6 to 10 seconds.

---

## 🤝 Contribution Guidelines

1.  Create a branch for your proposed skill/refactor: `git checkout -b feature/new-skill-name`.
2.  Add your skill inside the `skills/` folder following the standard layout.
3.  Run validation locally: `python3 scripts/validate.py`.
4.  Commit using conventional commit messages: `git commit -m "feat(skills): add new-skill-name"`.
5.  Submit a Pull Request. CI will run validation automatically.
