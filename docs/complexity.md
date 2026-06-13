# Agent complexity analysis

Composite score **1–5** per sheep:

- **Skills** — linked docs the agent reads
- **Lines to read** — agent + those docs (measured)
- **Context breadth** — artifacts, cross-step dependencies
- **Work difficulty** — cognitive load and operational risk

Scale: **1** = trivial · **5** = heaviest

Agent spawns use `sheep-*` names; skills keep legacy folder names (`subtask-maker`, etc.).

---

## Summary table

| Agent | Skills | Lines | Score | One-line summary |
|-------|--------|-------|-------|------------------|
| **nicki** | 6 | **486** | **3** | Orchestrator — `routing.yaml` + status read schemas; never loads sheep agents. |
| **sheep-start** | 1 | 175 | **3** | Worktrees, branch naming, sole `global-status.json` writer. |
| **sheep-spec** | 2 | **280** | **3** | Story → bounded YAML spec; light repo read. |
| **sheep-subtask** | 3 | **185** | **3** | Spec → ordered checklist; terse body. |
| **sheep-execute** | 3 | **368** | **5** | Only code-implementing sheep — edits, shell, strict scope. |
| **sheep-review** | 4 | 409 | **4** | Verify diff; review + `validation-format.md` in one spawn. |
| **sheep-sync** | 3 | 333 | **3** | Commit, merge `main` into feature, push feature branch. |
| **sheep-integrate** | 3 | 320 | **3** | Merge feature into `main`, push `main`. |
| **sheep-close** | 3 | **185** | **3** | Archive (report + story), erase spec/subtasks, unregister, delete worktree. |
| **sheep-status** | 3 | **372** | **3** | Writes only `status.json`; schema-heavy. |

### Skill-only (not a separate spawn)

| Skill | Lines | Notes |
|-------|-------|-------|
| `validation/validation-format.md` | 77 | Loaded by `sheep-review` — readiness + out-of-scope next-steps |
| `task-archive/archive-format.md` | 106 | Loaded via task-archive/SKILL.md in close flow |

---

## Tier snapshot

```
5 █    sheep-execute
4 █    sheep-review
3 ██████ nicki, sheep-start, sheep-spec, sheep-subtask, sheep-sync, sheep-integrate, sheep-close, sheep-status
```

---

## Reader/writer split (pattern)

Each artifact: **one writer** loads full `*-format.md`; **readers** load slim `*-input.md` or `*-read.md`. Disk artifact is the contract.

| Artifact | Writer | Full schema | Reader doc | Readers |
|----------|--------|-------------|------------|---------|
| Spec YAML | sheep-spec | `spec-format.md` | `spec-input.md` | sheep-subtask |
| Subtask MD | sheep-subtask | `subtask-format.md` | `subtask-input.md` | sheep-execute |
| status.json | sheep-status | `status-format.md` | `status-read.md` | nicki |
| global-status.json | sheep-start, sheep-close | `global-status-format.md` | `global-status-read.md` | nicki, sheep-status |

---

## Subtask load: trimmed

| Era | Docs loaded | Lines |
|-----|-------------|-------|
| Before | agent + SKILL + subtask-format + spec-format + caveman | **416** |
| **current** | agent + SKILL + subtask-format + spec-input | **185** |

Net: **~231 fewer lines** (~56%).

---

## Execute + status + nicki load: trimmed (2026-06-12)

| Agent | Before | After | Savings | Change |
|-------|-------:|------:|--------:|--------|
| **sheep-execute** | 394 | **368** | 26 | `subtask-input.md` replaces `subtask-format.md`; slim agent |
| **nicki** | 652 | **486** | **166** | `status-read.md` + `global-status-read.md` replace full status schemas |
| **sheep-spec** | 299 | **280** | 19 | Slim agent shell only |
| **sheep-status** | 394 | **372** | 22 | `global-status-read.md` replaces full global schema for read |

**New reader docs:** `subtask-input.md` (43), `status-read.md` (52), `global-status-read.md` (36).

---

## Review load: why it grew, then trimmed

| Era | Spawns | Docs loaded | Lines |
|-----|--------|-------------|-------|
| review + triage | 2 | 6 + 8 format schemas | **~1,543** |
| review inlined validation (bloated) | 1 | 10 docs incl. spec/subtask/execution formats + 3 validation files | **~965** |
| **current** | 1 | 5 docs: review SKILL + review/guidance formats + validation-format | **409** |

Growth was stacking validation on top of the old review load without cutting anything. Fix:

- One `validation-format.md` (procedure + schema + next-step shape) — not SKILL + 3 files
- Dropped `spec-format`, `subtask-format`, `execution-format` from agent load — review reads artifacts, does not need full format schemas
- Removed separate `out-of-scope` agent/step — folded into validation in same spawn

Net vs triage era: **~1,132 fewer lines**, one fewer spawn. Net vs pre-triage review-only (~703 lines): **~292 fewer** with validation included.

---

## Git tail (consolidated)

| | Before | After |
|---|--------|-------|
| Agents | commit, push, merge, publish | sync, integrate |
| Steps | 4 | 2 |
| Doc lines (approx.) | ~996 | ~662 |
| User confirms | 4 | 2 |

---

## Pipeline

```
start → describe → spec → subtasks → execute → review → acceptance → sync → integrate → close
```

Nicki-only: `describe`, `acceptance`, `fix`. Validation (readiness + next-steps) runs inside `review`.

---

## Do not trim further

| Agent | Lines | Why |
|-------|------:|-----|
| **sheep-review** | 409 | Reference implementation; validation merged |
| **sheep-close** | 185 | Archive = `docs/archive/<slug>/` (report.yaml, report.md, story.md) |
| **sheep-start** | 175 | Single SKILL; agent-only registry script |
| **sheep-sync** / **sheep-integrate** | 333 / 320 | `conflict-resolution` intentionally duplicated |

---

## Takeaways

1. **Peaks** — `sheep-execute` (implement), `sheep-review` (verify + validate).
2. **Load list, not folder size** — writer vs reader docs; disk artifact is the contract.
3. **Git tail** — sync + integrate halved confirms and agents.
4. **No out-of-scope sheep** — deferred `[scope]` handled in validation step inside review.
5. **Close archive** — three files under `docs/archive/<slug>/`; spec and subtasks erased, not copied.
6. **Cumulative trim** — subtask −231, nicki −166, execute/spec/status −67 combined.

---

*Measured 2026-06-12. Re-run line counts when agent load lists change.*
