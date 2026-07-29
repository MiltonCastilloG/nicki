# Flexibility — next steps

Date: 2026-07-29. Shipped baseline: [`flexibility.md`](flexibility.md).
Gate history: [`harness-gate-bugs.md`](harness-gate-bugs.md).

Sequenced flexibility work (ad-hoc, jump, drop `completed_steps`, materialize
same-suffix prerequisites) is **done**. This file is the backlog for what remains.

---

## 1. Jump format blocker (product)

**Doc:** [`jump_blocker.md`](jump_blocker.md)

Brainstorm (and other) `.md` design docs cannot jump to `subtasks` because the
spec slot expects `.json` and the harness does not convert. Real-use gap for
“bring my design and skip to checklist.”

**Unblock later** with one of: Nicki-mediated convert → JSON then jump; harness
convert; or relax gates for markdown specs. Not started.

---

## 2. Finding 5 — quoting / format hygiene (optional)

**Source:** [`harness-gate-bugs.md`](harness-gate-bugs.md) Finding 5

Sheep/format docs still lack a clear quoting rule for hand-authored structured
files. Impact is capped (`check-gate.py` denies cleanly; bootstrap soft-fails).
Polish only — not a flexibility gate.

---

## 3. CI for smoke suite (hygiene)

`python3 test.py` is the entrypoint; nothing runs it automatically.
`harness-alignment-subagents.md` once mentioned `./test.sh` (stale).

**Done when:** CI (or a documented hook) runs `python3 test.py` on PRs/pushes.

---

## 4. Dogfood (validation)

Manual pass on a real task:

- Ad-hoc sync mid-`execute` (position unchanged, `side_effects` + archive row)
- Same-format jump (e.g. existing JSON spec → `subtasks`; JSON execution → `review`)

Confirms Nicki prose (`nicki.md` Ad-hoc / Jump) matches operator expectations.

---

## Explicitly out of scope here

- Rewriting frozen `docs/archive/**` beyond historical banners (done 2026-07-29)
- Re-opening closed gate findings 1–4, 6–7
- Expanding `adhoc_allowed` / jump targets unless a new product need appears
