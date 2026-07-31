# Flexibility — next steps

Date: 2026-07-31. Shipped baseline: [`flexibility.md`](flexibility.md).
Gate history: [`harness-gate-bugs.md`](harness-gate-bugs.md).

Sequenced flexibility work (ad-hoc, jump, drop `completed_steps`, informal jump,
drop execution artifact, drop sequence / `--override`) is **done**. This file is
the backlog for what remains.

---

## 1. Jump format blocker — **closed**

**Doc:** [`jump_blocker.md`](jump_blocker.md) (resolved).
**Design:** [`superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md`](superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md).

Informal jump + drop execution shipped in harness / `.cursor`: jump is
position-only (no materialize / suffix match); chat is enough; sheep accept
whatever Nicki passes; execute omits `artifact`; review never requires
execution JSON. Harness still does not convert markdown→JSON (non-goal).

---

## 2. Drop sequence denials and `--override` — **done** 2026-07-31

**Design:** [`superpowers/specs/2026-07-31-drop-sequence-and-override-design.md`](superpowers/specs/2026-07-31-drop-sequence-and-override-design.md).
Also recorded in [`flexibility.md`](flexibility.md) Decision 6 / sequencing row 12.

Removed `deny_sequence` / `SEQUENCE`, sync acceptance ordering, done-before-close,
the gate waiver path, and `--override`. Acceptance before first sync is Nicki
chat confirm only. Adhoc/jump remain for write semantics and policy bookends.

---

## 3. Finding 5 — quoting / format hygiene (optional)

**Source:** [`harness-gate-bugs.md`](harness-gate-bugs.md) Finding 5

Sheep/format docs still lack a clear quoting rule for hand-authored structured
files. Impact is capped (`check-gate.py` denies cleanly; bootstrap soft-fails).
Polish only — not a flexibility gate.

---

## 4. CI for smoke suite (hygiene)

`python3 test.py` is the entrypoint; nothing runs it automatically.
`harness-alignment-subagents.md` once mentioned `./test.sh` (stale).

**Done when:** CI (or a documented hook) runs `python3 test.py` on PRs/pushes.

---

## 5. Dogfood (validation)

Manual pass on a real task:

- Ad-hoc sync mid-`execute` (position unchanged, `side_effects` + archive row)
- Informal jump (e.g. chat / design `.md` → `subtasks` or `review` with no
  predecessor file; `current_step` unchanged, `next_step` = target)

Confirms Nicki prose (`nicki.md` Ad-hoc / Jump) matches operator expectations.

---

## Explicitly out of scope here

- Rewriting frozen `docs/archive/**` beyond historical banners (done 2026-07-29)
- Re-opening closed gate findings 1–4, 6–7
- Expanding `adhoc_allowed` / jump targets unless a new product need appears
- Harness markdown→JSON conversion (still a non-goal)
