# Shinobu

TDD pipeline. A **different product and repository**, created as a history-preserving fork of Nicki after Nicki Stage 1 and the host-neutral runtime extract. Invoked by name: `shinobu …`.

It inherits Nicki's mechanics at the fork point: one sheep at a time, disk handoffs, caller-owned paths, `sheep-status` after every sheep except `sheep-start` and `sheep-close`, `normal` / `jump`, stop-and-ask. One intentional exception: the final test and implementation refactor sheep run in parallel.

Stages: [`SHINOBU_NEXT_STEPS.md`](SHINOBU_NEXT_STEPS.md).

---

## Fork boundary

Saying **Shinobu** is the selector in the Shinobu repository. There is no `--pipeline` flag and no pipeline field. Nicki and Shinobu do not coexist in one runtime and do not share live files after the fork.

| Shinobu owns after the fork | Inherited baseline (independent copy) |
| --------------------------- | ----------------------------------- |
| `workflow-runtime/agents/shinobu.md` | Leaf sheep: spec, Gherkin, review, sync, archive, integrate, fallback |
| Shinobu routing and bootstrap | Leaf skills: `spec-maker`, `story-maker`, review and git skills |
| Red, green, test-refactor, implementation-refactor sheep and skills | Start/status/close sheep and scripts |
| Shinobu installer text, workspace/config/version names | `status.json`, `story.md`, `specs/`, worktree/archive layout |

Repository identity is the namespace. Agents stay flat and retain ordinary names (`sheep-start`, `sheep-status`, `sheep-close`). Artifacts remain generic (`status.json`, `story.md`, `specs/`). Product prefixes used only to avoid same-repo collisions are cancelled.

A worktree belongs to whichever repository created it.

**Stage 1 happens in Nicki** (spec-first, Gherkin-as-transform). The neutral runtime is extracted next; only then is the repository forked. Shinobu inherits that exact tagged baseline.

---

## Sheep

### New

| Sheep | Input | Output |
| ----- | ----- | ------ |
| `sheep-red` | **One Gherkin scenario** (Shinobu packs it — id + body — the way it packs a spec path). Worktree as scope. | Step definitions + a run. Success: the test **fails right**. Anything else is an **error** (`open_questions`); the loop stops. |
| `sheep-green` | **The git diff only** (uncommitted tree after red). | Smallest change that makes the failing test pass. Does not edit the test. Does not touch the story checklist. |
| `sheep-test-refactor` | **The post-loop git diff.** | Revises tests only: simplify, remove duplication, and improve test abstractions without changing scenario meaning. Exact test-file scope is deliberately open until build time. |
| `sheep-implementation-refactor` | **The post-loop git diff.** | Revises implementation only: simplify, remove duplication, and improve implementation abstractions without changing behavior. Exact implementation-file scope is deliberately open until build time. |

Existing step-definition files are just code in the worktree. Red sees them the way execute sees existing source — it does not need a pointer. Shinobu's job is to pack the **next scenario** into red, not to teach red where steps live.

### Modified

| Sheep | Change |
| ----- | ------ |
| `sheep-gherkin` | Reads the **spec**. Writes Gherkin **as a checklist** (`- [ ]` per scenario), ordered by dependency. Split before ordering if a scenario cannot be summarized in two sentences, reads like a goal, or has **more than four `Then` clauses**. Amend appends a new `- [ ]`. **No product questions** — incomplete spec → Shinobu sends `sheep-spec` again. |

### Inherited leaf sheep

`sheep-spec`, `sheep-gherkin`, `sheep-review`, `sheep-sync`, `sheep-archive`, `sheep-integrate`, `sheep-fallback`.

`sheep-spec` is unchanged. It already accepts free text / `task.original`.

### Lifecycle inherited at fork

Start, status, and close retain the generic names `sheep-start`, `sheep-status`, and `sheep-close`. They are copied with the repository, then maintained independently. Shinobu rewrites product-facing routing/bootstrap/configuration and has no Nicki runtime dependency.

### Not used by Shinobu

`sheep-subtask`, `sheep-execute` — Nicki's tail. Remove them from the Shinobu fork when red/green replaces them.

---

## Questions live on spec

`sheep-spec` already stops on vague outcome, unclear scope, competing interpretations, and design forks (`spec-maker` Step 2). `sheep-gherkin` does not ask. The orchestrator does not interview at gherkin.

---

## Scenario checklist (the cursor)

`sheep-gherkin` writes the Gherkin **as a checklist**, same idea as Nicki subtasks: one `- [ ]` per scenario, ordered by dependency. That file **is** the cursor. No extra field on status.

- The **loop** (Shinobu, programmatically — not a sheep) picks the first `- [ ]` and packs that scenario into red.
- After green returns success, the **same loop** marks that line `- [x]`. Green never edits the story. Exact flip mechanism is for when the loop is built.
- **Exit:** no `- [ ]` left → parallel test and implementation refactors.
- Amend appends a new `- [ ]`. The loop will pick it up; earlier `- [x]` stay done.

`status.json` still holds `current_step` / `next_step` / artifact pointers / `open_questions`. It does not store which scenario is next — the story file does.

---

## Loop runs uninterrupted

After the yes before the first red, Shinobu runs red → green for every remaining scenario, then both refactor sheep in parallel, then review, **without asking and without a timer**.

Red and green each do **one write and one run of this scenario**, then return (`task: false`). `open_questions` still stops on a real error (red failed wrong, etc.). The user is not polled between them.

The two refactor sheep are one logical parallel stage. They receive the same post-loop diff and must not touch each other's file domain. Shinobu waits for both, sends one aggregate status update, then review performs the authoritative final verification. Exact scope boundaries remain open until these sheep are built.

---

## Order

`sheep-status` runs after every sheep except `sheep-start` and `sheep-close`, and writes `status.json`. The parallel refactor pair produces one aggregate status update after both return.

1. `sheep-start`
2. `sheep-spec` → `specs/`
3. `sheep-gherkin` → `story.md` checklist
4. **Human gate** — approve the scenarios
5. **Consent once**, then the loop until the checklist is clear:
   1. `sheep-red` — packed first `- [ ]` scenario
   2. `sheep-green` — diff
   3. loop marks that scenario `- [x]` (programmatic; not a sheep)
6. In parallel:
   1. `sheep-test-refactor` — post-loop diff; test domain only
   2. `sheep-implementation-refactor` — post-loop diff; implementation domain only
7. `sheep-review`
8. **Human gate** — user sees the uncommitted changes, then git tail
9. Git tail:
   1. `sheep-sync`
   2. `sheep-archive`
   3. `sheep-sync`
   4. `sheep-integrate`
   5. `sheep-close`

Two consents only: before the first red, after review. Nothing in the loop or parallel refactor stage asks or commits.

When something is wrong, jump to gherkin and **append** a new scenario. If the spec is wrong, jump to spec.

---

## Red is binary

One success: the test **fails right**. Pass on arrival, broken setup, or wrong failure → `open_questions`, loop held. User and Shinobu look at it; red is re-spawned with the same scenario. Errors should be rare.

---

## Black sheep (later)

`black-sheep-*` = ad-hoc only, never a pipeline step. Inverse of the product lifecycle sheep (orchestrator-only). Membership is the black-sheep audit's output, not decided here.

First build after the audit: `black-sheep-testing-scaffold` (Gherkin runner + step-definition layout). Until then, Shinobu only runs where a runner already exists.

---

## What stays the same (reused, not copied)

Spec schema and pause, output/archive paths, modes, git tail, stop-and-ask, fallback, worktree layout, and registry are inherited at the fork point. They are independent copies afterward.
