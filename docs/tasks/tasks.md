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

## Next (before Shinobu fork)

| # | Task | Notes |
|---|------|-------|
| **20** | **Approach B: host-neutral runtime extract** | Move committed agents/skills/rules out of `.cursor/` into `workflow-runtime/`; keep agents flat and skills one level deep; flip `RUNTIME_ROOT`; add Cursor-side adapter install. Checklist: [`host-runtime-backlog-and-approach-b.md`](host-runtime-backlog-and-approach-b.md). Design: [`2026-07-15-host-runtime-single-source-design.md`](2026-07-15-host-runtime-single-source-design.md). Approach A shipped — [`tasks-done.md`](tasks-done.md). |

Path: [`SHINOBU_NEXT_STEPS.md`](../SHINOBU_NEXT_STEPS.md) · ownership: [`OWNERSHIP.md`](../OWNERSHIP.md).

---

## Later / deferred

| Item | Notes |
|------|-------|
| PLAN CLI + multi-project dogfood | [`PLAN.md`](../PLAN.md) — schema, `workspace init` / clone / install / doctor, dogfood across managed projects |
| **17** AWS deployment exploration | How TBD. Candidate: [Bedrock AgentCore MCP](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-getting-started.html). Document options; no playbook yet. |
| Caller-owned output shape | [`caller-owned-output-shape.md`](caller-owned-output-shape.md) — defer all-sheep redesign until Stage 2 sheep exist; archive-only bugs if they bite |
| Shinobu Stage 2+ | Fork after #20, then TDD loop. [`SHINOBU.md`](../SHINOBU.md) · [`SHINOBU_NEXT_STEPS.md`](../SHINOBU_NEXT_STEPS.md) |
| Quoting polish | Optional only — [`story-format.md`](../../.cursor/skills/story-maker/story-format.md). Not a rewrite. |

---

## References

| Doc | Role |
|-----|------|
| [`tasks-done.md`](tasks-done.md) | Shipped tasks and archives |
| [`flexibility.md`](flexibility.md) | Flexibility model (shipped) |
| [`NICKI.md`](../NICKI.md) | Workflow semantics |
| [`WORKFLOW-DIAGRAMS.md`](../WORKFLOW-DIAGRAMS.md) | Pipeline diagrams |
| [`SHINOBU_NEXT_STEPS.md`](../SHINOBU_NEXT_STEPS.md) | Stages + sequencing |
