---
name: New skill proposal
about: Propose a new agent skill, instruction reference, or best practice matrix
title: '[PROPOSAL] '
labels: enhancement, skill-proposal
assignees: ''

---

**1. Skill Name**
Provide a proposed short name for the skill (e.g. `gemini-omni-audio-sync`).

**2. Goal / Functional Scope**
What task or feature will this skill help agents execute? What user intents will it trigger on?

**3. Proposed Structure**
Will this skill consist of a single `SKILL.md` or require sub-references (Level 3 optimization)? Outline the folder structure below:
```text
skills/your-skill-name/
├── SKILL.md
└── references/
    └── your_reference.md
```

**4. Example Trajectory / Target Behavior**
Provide a short example of a user query and the expected agent behavior or prompt modification when this skill is active.

**5. Additional Info**
Are there specific SDK documentations or API guidelines that this skill should be modeled after?
