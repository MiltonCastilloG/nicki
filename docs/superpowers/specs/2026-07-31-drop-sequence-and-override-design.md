# Design: Drop sequence denials and `--override`

Date: 2026-07-31  
Status: **implemented** (plus follow-up dead-surface cleanup the same day)  
Related: [`docs/flexibility.md`](../../flexibility.md), [`docs/flexibility_next_steps.md`](../../flexibility_next_steps.md), [`docs/harness-gate-bugs.md`](../../harness-gate-bugs.md)

## Problem

1. `deny_sequence` / `gate_class: sequence` exist so `--override`, `--mode adhoc`, or `--mode jump` can waive ordering denials. Only two sequence denials remain: sync must sit on acceptance (or have archive), and `done` must follow `close`.
2. `--override` is a blunt leftover that waives the same sequence class. Adhoc and jump already cover real flexibility (write semantics + historical “sync without acceptance”). Override historically papered over broken gates (`harness-gate-bugs.md`).
3. Acceptance-before-sync is a product checkpoint Nicki can enforce in chat; the gate does not need to encode it as waivable ordering.

## Goal

- Eliminate **`deny_sequence`**, **`SEQUENCE`**, and the sequence waiver path entirely.
- Eliminate **`--override`**.
- Every gate denial is final — no flag waives a deny. Consent and readiness stay hard.
- Acceptance before first sync is **Nicki ask/confirm in chat only**.
- Keep `--mode adhoc` / `--mode jump` for **write** semantics only (position stay vs set `next_step`).

## Constraints (unchanged)

| Constraint | Means |
|---|---|
| Scripts stay authoritative | Gate and status scripts keep the veto |
| Safety / consent never waived | Missing inputs, readiness blocks, `user_confirm_required` still deny with no bypass flag |
| Modes own write shape | `adhoc` / `jump` still change how `update-status.py` moves position — they are not “waiver modes” after this change |

## Decision summary

| Topic | Decision |
|---|---|
| `deny_sequence` / `SEQUENCE` | **Remove** |
| `--override` | **Remove** from CLI, Nicki prose, permissions, smokes |
| Sync acceptance ordering | **Remove** from `gate_sync`; Nicki asks/confirms in chat |
| Done-before-close ordering | **Remove** from `gate_done` (delete empty gate if nothing left) |
| `gate_policy.classes.sequence` + `sequence_denials` | **Remove** from `routing.json` |
| Gate deny after change | All denials are non-waivable (`deny` only; `gate_class` may stay as `"safety"` or drop to null-only-on-allow — pick one and keep smokes consistent) |
| Adhoc / jump on the gate | No longer waive anything; policy bookends remain (`adhoc_allowed`, jump cannot target `start`/`close`/`done`) |

## Gate / harness changes

### `gates.py`

- Delete both `deny_sequence(...)` call sites.
- `gate_sync`: keep readiness / blocked checks; drop `current_step == acceptance` / archive sequence branch.
- `gate_done`: remove or delete if it only existed for that sequence check.
- Drop `deny_sequence` import.

### `gate_utils.py`

- Remove `SEQUENCE` and `deny_sequence()`.
- Keep `deny()` / `allow()`. If `gate_class` remains on stdout, denials are always safety (or stop emitting a class distinction — document the chosen contract in `check-gate.py` docstring).

### `check-gate.py`

- Remove `--override` argument and `override` parameter plumbing.
- Remove waiver branch (`gate_class == SEQUENCE` + override/adhoc/jump → allow with waived reason).
- Docstring: denials are never waived; modes are echoed for write forwarding only.
- Keep `_policy_denial` for jump bookends, adhoc_allowed, and `user_confirm_required`.

### `routing.json`

- Rewrite sync `gate` prose: consent + readiness; no “acceptance or override.”
- Remove `gate_policy.classes.sequence` and `sequence_denials` (and the smoke that diffs that list against `deny_sequence` calls).
- Soften or rewrite `safety` class text so it no longer mentions override / sequence waiver.

## Nicki / product

- Before first sync: present acceptance summary; proceed only after explicit user accept in chat. Do not rely on (or mention) `--override` or sequence waiver.
- Mid-pipeline “sync now”: still `--mode adhoc` so the **write** leaves position untouched; gate no longer needs a sequence waive for acceptance ordering.
- Flags section: drop `--override` and “`gate_class: sequence` means waive.” On deny: fix the cause or stop.
- Sync step blurb: drop “or on override.”

## Docs

- `docs/flexibility.md` — constraints and mode table: no sequence waiver; no `--override`; modes are write semantics; acceptance is chat-only.
- `docs/flexibility_next_steps.md` — backlog entry for this work until shipped.
- `docs/NICKI.md`, `.cursor/agents/nicki.md`, `.cursor/permissions.json` — strip override / sequence-waiver language.
- `docs/harness-gate-bugs.md` — optional one-line note that sequence class / override were removed (do not rewrite frozen archive stories).

## Tests

Update `tests/smoke/gates_matrix.py` (and any override-only cases):

- Sync without acceptance + `--user-confirmed` + readiness ok → **allow** (no waive reason).
- Remove cases that assert “waived by --override” / done sequence waived by override.
- Keep: override-equivalent consent failures become “no override flag”; consent still required; readiness still blocks sync; jump cannot target close; adhoc denied on start/close/done.
- Remove `sequence_denials` ↔ `deny_sequence` parity check.

`python3 test.py` remains the entrypoint.

## Non-goals

- Changing adhoc/jump **write** behavior.
- Removing `adhoc_allowed` or jump bookend policy.
- Softening consent or readiness blocks.
- Rewriting frozen `docs/archive/**` stories that mention override historically.

## Acceptance

- No `deny_sequence`, `SEQUENCE`, or `--override` in harness scripts.
- No sequence waiver path in `check-gate.py`; allow reasons never say “sequence check waived.”
- Sync gate does not require `current_step == acceptance`.
- Nicki prose: acceptance is chat confirm; no override flag instructions.
- Smokes above pass via `python3 test.py`.
