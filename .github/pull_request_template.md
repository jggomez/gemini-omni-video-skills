## Description
Please describe the changes in this Pull Request, detailing any new skills, reference guides, or enhancements added.

## Type of Change
- [ ] New agent skill (`skills/new-skill`)
- [ ] Update or refactor to an existing skill/reference
- [ ] Maintenance (validator scripts, workflows, documentation)
- [ ] Bug fix (non-breaking change resolving an issue)

## Checklist
Before submitting this PR, please check that you have completed the following:

- [ ] The folder name in `skills/` matches the `name` field in the `SKILL.md` frontmatter exactly.
- [ ] The `SKILL.md` contains all required frontmatter metadata fields:
  - `name`
  - `description`
  - `version`
  - `author`
  - `category`
  - `tags`
- [ ] All code blocks (triple-backticks) are properly closed and formatted.
- [ ] Any references in `references/` subdirectory are valid and links pointing to them are correct.
- [ ] The local validation script was run and passed successfully:
  ```bash
  python3 scripts/validate.py
  ```
- [ ] The changes maintain standard markdown and github-flavored markdown syntax.
