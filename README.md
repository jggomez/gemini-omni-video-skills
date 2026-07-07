# Gemini Omni Video Skills

A production-ready library of agent skills designed to orchestrate video generation, structured prompting, and stateful video editing with Gemini Omni Flash (`gemini-omni-flash-preview` / `bouncybohr`).

These skills are optimized for **Progressive Disclosure** to keep token usage low while giving LLM agents full access to advanced generation patterns, parameters, and workflows.

[![Validate Skills](https://github.com/your-username/gemini-omni-video-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/your-username/gemini-omni-video-skills/actions/workflows/validate-skills.yml)
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

### Option A: Local Symlinking (Recommended for Development)
Symlink this repository's folders into your agent's local skills directory (typically under `~/.gemini/skills/` or equivalent):

```bash
ln -s "$(pwd)/skills/gemini-omni-flash" ~/.gemini/skills/gemini-omni-flash
ln -s "$(pwd)/skills/gemini-omni-prompt-architect" ~/.gemini/skills/gemini-omni-prompt-architect
ln -s "$(pwd)/skills/vibe-video-prompt-engineering" ~/.gemini/skills/vibe-video-prompt-engineering
```

### Option B: Configuration Declaration
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

## 🧪 Validating Skills Locally

Before pushing changes to GitHub, run the validation tool to ensure the skill formats, YAML frontmatter, code blocks, and internal references are free of syntax and structural errors:

```bash
python3 scripts/validate.py
```

### Skill Specification Standard
Every skill must adhere to the following directory layout and metadata structure:

1.  **Directory Name:** Match the lowercase, hyphenated `name` field in the frontmatter.
2.  **`SKILL.md`:** Must reside in the skill root directory.
3.  **Frontmatter:** Must be defined at the top of `SKILL.md` using valid YAML block boundaries:
    ```yaml
    ---
    name: name-of-your-skill
    description: Concise description of when to use this skill
    version: 1.0.0
    author: Author/Org
    category: functional-category
    tags: [tag1, tag2]
    ---
    ```
4.  **Syntax Verification:**
    *   All code blocks (```language ... ```) must be correctly opened and closed.
    *   Any relative file paths starting with `references/` (e.g., `references/text_to_video.md`) must resolve to valid physical files in the skill's subdirectory.

---

## 🤝 Contribution Guidelines

1.  Create a branch for your proposed skill/refactor: `git checkout -b feature/new-skill-name`.
2.  Add your skill inside the `skills/` folder following the standard layout.
3.  Run validation locally: `python3 scripts/validate.py`.
4.  Commit using conventional commit messages: `git commit -m "feat(skills): add new-skill-name"`.
5.  Submit a Pull Request. CI will run validation automatically.
