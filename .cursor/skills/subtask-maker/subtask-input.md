# Subtask input (read-only)

Markdown checklist at `current-task/subtasks/<slug>.md`. Execute-plan **reads** and may flip `- [ ]` → `- [x]` only. Writer schema: [subtask-format.md](subtask-format.md).

## File structure

1. YAML frontmatter — metadata.
2. `# Subtasks` heading.
3. Ordered checklist — `- [ ]` pending, `- [x]` complete.

## Frontmatter to read

| Field | Use |
|-------|-----|
| `worktree` | Must match worktree slug |
| `spec` | Load for `scope.out` checks when present |
| `constraints` | Respect during execution (e.g. `no-commit`, `no-new-deps`) |
| `context` | Traceability only |

## Checklist rules

- Process **unchecked** lines top to bottom; mark `- [x]` before moving on.
- Skip lines already `- [x]` (resume).
- One sentence per line — stop and ask if vague or out of spec scope.
- Verification lines last (`Run npm run lint`, etc.) — run before marking complete.

## Minimal shape

```markdown
---
worktree: hero-section
spec: current-task/specs/hero-section.yaml
constraints:
  - no-commit
---

# Subtasks

- [ ] Implement a Hero component with headline, subcopy, and a primary CTA.
- [ ] Run npm run lint on changed files and fix any issues.
```

**Edit boundary:** flip checklist state only — do not rewrite subtask text without user approval.
