# Review format

**JSON only** — output reviews have exactly two top-level keys: `approved` and `content`.

Default path: `current-task/reviews/<slug>.json` under the worktree scope root.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `approved` | Yes | `true` if the implementation passes review; `false` if blocking issues remain |
| `content` | Yes | Pass summary (`approved: true`) or actionable issue list (`approved: false`) |

**Output reviews have no other top-level keys.** Do not add `meta`, `title`, or routing hints.

## Optional review input (guidance)

Review guidance files use review JSON plus one extra input-only key. See [review-guidance-format.md](review-guidance-format.md).

| Field | Required | Description |
|-------|----------|-------------|
| `approved` | Yes | Usually `false`; explains that previous review should not be treated as approved |
| `content` | Yes | Why the previous review should be rerun |
| `important-considerations` | Yes | Scope or correctness notes to keep in mind while reviewing |

`important-considerations` is input-only. Output must still have only `approved` and `content`.

## `approved`

- `true` — requirements met, subtasks satisfied, verify passed, no blocking convention violations. `[scope]` notes allowed.
- `false` — one or more **blocking** issues (`[req-`, `[subtask:`, `[verify]`, `[convention]`). `[scope]` alone does not require `false`.

## `content`

Use a JSON string (use `\n` for newlines). Write in plain language with consistent prefixes so issues are easy to scan and act on.

### When `approved: true`

Brief pass summary (2–5 lines). Mention requirements coverage, verify results, and scope.

```json
{
  "approved": true,
  "content": "All spec requirements met (hero-headline, hero-subcopy, hero-cta, hero-tokens).\nChecked subtasks for Hero implementation and page wiring are complete.\nVerify: npm run lint and npm test -- Hero passed.\nNo files changed outside spec scope.\n"
}
```

### When `approved: false`

List **blocking issues** only. Each bullet should be actionable — reference IDs, paths, and failures.

| Prefix | Use for |
|--------|---------|
| `[req-<id>]` | Spec requirement not met |
| `[subtask:<index>]` | Checked subtask not done or done incorrectly |
| `[scope]` | Change outside spec `scope.out` — **non-blocking**; validation skill may write `next-steps/*.json` |
| `[verify]` | Lint, test, build, or other check failure |
| `[convention]` | CONTRIBUTING rule violation (tokens, i18n, deps) |

```json
{
  "approved": false,
  "content": "[req-hero-cta] Hero component has no CTA button — only headline and subcopy rendered.\n[subtask:2] app/page.tsx still imports LandingBanner; Hero not wired in.\n[verify] npm run lint failed: src/components/Hero/Hero.tsx — unused import 'Link'.\n[scope] src/components/Footer/Footer.tsx modified — outside spec scope.out.\n"
}
```

## Writing good `content`

**Do:**

- Reference spec requirement IDs and subtask indices when applicable
- Name exact file paths for code and scope issues
- Paste or summarize verify command failures with enough context to reproduce
- Keep bullets specific and testable

**Don't:**

- Suggest fixes or checklist rewrites — only report what failed review
- Include non-blocking nits unless strict review was requested
- Add keys beyond `approved` and `content`

## Ambiguity → ask

Ask before writing the review when:

- Spec or subtask list is missing and partial review is insufficient
- A requirement is subjective and pass/fail is unclear
- Verify commands cannot run (missing deps, wrong branch base)
- Git history makes change discovery unreliable

Resolve or get user direction, then write the review file.
