# Jump blocker — prerequisite format mismatch

Date: 2026-07-29. Related: [`flexibility.md`](flexibility.md) Capability B / B4.

## Real-use case

User has a design doc from `brainstorm` (markdown under `docs/superpowers/specs/…`) and wants to **jump to `subtasks`**.

Today:

1. Jump requires the **predecessor** artifact to already match routing’s expected suffix.
2. Predecessor of `subtasks` is `spec` → expected `current-task/specs/<slug>.json`.
3. Brainstorm output is `.md`.
4. Harness **rejects** the jump (`jump artifact must be .json …`) — no markdown→JSON conversion.

So the user cannot “bring my brainstorm and skip to checklist” without first producing a schema-shaped JSON spec (manually, via Nicki chat rewrite, or by running the normal `spec` sheep).

That is a **product blocker** for the common external-input path, even though jump + materialize work when the format already matches.

## Why YAGNI left it this way

| Approach | Cost | Status |
|---|---|---|
| Convert md→JSON in harness | Changes how “spec” is defined; shape/open_questions rules; tests | Deferred — too much complexity now |
| Accept `.md` as `artifacts.spec` | Breaks `gate_subtasks` / `load_artifact` (JSON/YAML objects only) | Not viable without gate changes |
| Require correct suffix + copy into `current-task/` | Small; archive-safe when format matches | **Shipped** |

Shipped behavior is correct for same-format jumps (e.g. an existing JSON spec or execution handoff). It does **not** cover brainstorm → subtasks.

## What “done” would look like (not built)

Pick one later:

1. **Nicki-mediated convert** — before jump, Nicki (or `sheep-spec` with design-doc input) writes `current-task/specs/<slug>.json`, then jump/materialize.
2. **Harness convert** — jump accepts `.md` and emits schema JSON (defines the mapping).
3. **Relax gates** — allow markdown specs with a different validation path (larger contract change).

Until then: document the limit; Nicki should tell the user they need a JSON spec (or the normal spec step) before jumping to `subtasks`.

## Acceptance when unblocked

- Jump to `subtasks` with only a brainstorm `.md` path succeeds end-to-end (gate allows, sheep runs), **or** Nicki has a single explicit convert step that is part of the jump flow and covered by a smoke test.
- Materialized prerequisite still lives under `current-task/` for archive.
