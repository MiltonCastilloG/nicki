# Nicki — tasks

Actionable backlog. Completed work: [`tasks-done.md`](tasks-done.md).

## Three goals (always)

Every change must respect **all three**. They are standing requirements, not pick-one options.

| Goal | Always means |
|------|----------------|
| **Correct functioning** | Pipeline runs end-to-end; worktrees, paths, handoffs work |
| **Harness and guardrails** | Read/write scripts + smoke tests stay in place; scripts enforce position; chat consent for execute/sync |
| **Trimming** | Prompt and docs stay lean; cut duplication when safe |

**When goals conflict**, higher tier wins: (1) Correct functioning → (2) Harness and guardrails → (3) Trimming.

Example: never trim `nicki.md` consent rules that scripts do not enforce.

---

## Next — fork

Pre-fork list is **complete**: **20a** · **20b** · **20c** prose paths → `workflow-runtime/` · **21** path_resolution + rule_drift · docs pass — see [`tasks-done.md`](tasks-done.md). Rationale: [`2026-09-19-runtime-extract-and-delivery-options.md`](2026-09-19-runtime-extract-and-delivery-options.md).

Tag the Nicki baseline → clone with history into a sibling Shinobu repository → swap `origin`. Sequence: [`SHINOBU_NEXT_STEPS.md`](../SHINOBU_NEXT_STEPS.md) · ownership: [`OWNERSHIP.md`](../OWNERSHIP.md).

---

## Later / deferred

Nothing below blocks the fork. **22–25 are mutually independent — any or all can run in parallel, in either repo, before or after the fork.**

| # | Item | Notes |
|---|------|-------|
| **22** | PR-gated integrate | **Deferred at the fork, deliberately.** `sync` opens/updates the PR; `integrate` waits on checks, then merges (keep the local merge; do not switch to `gh pr merge`). Degrade to today's local merge when there is no remote or no `gh`. Conflicts stay local and human-approved; consent model unchanged. Adopt in either repo if a red merge ever actually happens. Design: §Layer D of the design note. |
| **23** | Runtime install into managed projects | `install.py --project projects/<name>` links/copies `workflow-runtime/` into that project's host dirs. Fixes observed staleness: `projects/tetris-clone-frp/.cursor/` has `skills/` and no `agents/`; the other two clones have no `.cursor/`. Build only if that is actually biting — see open question 3 in the design note. |
| **24** | Release artifact on tag | CI on `v*` builds a runtime tarball with **materialized** (copied, Windows-safe) host adapters, attached to a GitHub Release. The right shape of the "CI performs the adaptations" ambition; gives `nicki_version.yaml` meaning. Rejected alternative: committing generated adapters back to `main` (push→CI→push loop collides with the git tail). |
| **25** | Real-git worktree exercise in CI | `git init` fixture → start → status → close. Git is present in Actions, no remote needed. Largest unclaimed automation win. |
| **17** | AWS deployment exploration | How TBD. Candidate: [Bedrock AgentCore MCP](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-getting-started.html). Document options; no playbook yet. |
| | PLAN CLI + multi-project dogfood | [`PLAN.md`](../PLAN.md) — schema, `workspace init` / clone / install / doctor |
| | Caller-owned output shape | [`caller-owned-output-shape.md`](caller-owned-output-shape.md) — defer all-sheep redesign until Stage 2 sheep exist; archive-only bugs if they bite |
| | Shinobu Stage 2+ | After the fork: TDD loop. [`SHINOBU.md`](../SHINOBU.md) · [`SHINOBU_NEXT_STEPS.md`](../SHINOBU_NEXT_STEPS.md) |
| | Quoting polish | Optional only — [`story-format.md`](../../workflow-runtime/skills/story-maker/story-format.md). Not a rewrite. |

**Not doing:** `nicki_template` repo with cross-repo sync (revisit only if 24 proves insufficient) · shared runtime package, submodule, or subtree · Claude hook parity or generated Claude permissions adapter · branch protection on `main` · `nicki doctor` / version pin · evaluation harness or repository.

---

## References

| Doc | Role |
|-----|------|
| [`2026-09-19-runtime-extract-and-delivery-options.md`](2026-09-19-runtime-extract-and-delivery-options.md) | Extract, distribution, validation, and git-tail options |
| [`tasks-done.md`](tasks-done.md) | Shipped tasks and archives |
| [`flexibility.md`](flexibility.md) | Flexibility model (shipped) |
| [`NICKI.md`](../NICKI.md) | Workflow semantics |
| [`WORKFLOW-DIAGRAMS.md`](../WORKFLOW-DIAGRAMS.md) | Pipeline diagrams |
| [`SHINOBU_NEXT_STEPS.md`](../SHINOBU_NEXT_STEPS.md) | Stages + sequencing |
