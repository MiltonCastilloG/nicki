# Flexibility — next steps

Date: 2026-08-05. Shipped baseline: [`flexibility.md`](flexibility.md).
Gate history (historical): [`harness-gate-bugs.md`](harness-gate-bugs.md).
Spawn gate retired: [`superpowers/specs/2026-08-05-retire-check-gate-design.md`](superpowers/specs/2026-08-05-retire-check-gate-design.md).

Sequenced flexibility work (ad-hoc, jump, drop `completed_steps`, informal jump,
drop execution artifact, drop sequence / `--override`, retire check-gate,
ad-hoc as direct sheep invocation) is **done**. This file is the backlog for
what remains.

---

## 1. Jump format blocker — **closed**

**Doc:** [`jump_blocker.md`](jump_blocker.md) (resolved).
**Design:** [`superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md`](superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md).

---

## 2. Drop sequence denials and `--override` — **done** 2026-07-31

**Design:** [`superpowers/specs/2026-07-31-drop-sequence-and-override-design.md`](superpowers/specs/2026-07-31-drop-sequence-and-override-design.md).

---

## 3. Retire check-gate — **done** 2026-08-05

**Design / archive:** [`superpowers/specs/2026-08-05-retire-check-gate-design.md`](superpowers/specs/2026-08-05-retire-check-gate-design.md), [`archive/retire-check-gate/report.md`](archive/retire-check-gate/report.md).

Spawn veto deleted. Consent is Nicki chat for execute + sync only. `expected_artifact` removed from routing.

---

## 4. Ad-hoc is direct sheep invocation — **done** 2026-08-05

**Design:** [`superpowers/specs/2026-08-05-adhoc-direct-sheep-invocation-design.md`](superpowers/specs/2026-08-05-adhoc-direct-sheep-invocation-design.md).

`--mode adhoc` removed. Ad-hoc needs no task: the agent spawns the sheep directly and relays its return. Nicki keeps `normal` and `jump`.

---

## 5. Finding 5 — quoting / format hygiene (optional)

**Source:** [`harness-gate-bugs.md`](harness-gate-bugs.md) Finding 5 (historical; gate no longer parses sheep artifacts at spawn).

Sheep/format docs still lack a clear quoting rule for hand-authored structured
files. Polish only.

---

## 6. CI for smoke suite (hygiene)

`python3 test.py` is the entrypoint; nothing runs it automatically.

**Done when:** CI (or a documented hook) runs `python3 test.py` on PRs/pushes.

---

## 7. Dogfood (validation)

Manual pass on a real task:

- Ad-hoc sheep invoked directly with no task (runs, returns, writes no pipeline state)
- Informal jump (e.g. chat / design `.md` → `subtasks` or `review`)

Confirms the rule prose (`nicki-default.mdc` ad-hoc, `nicki.md` jump) matches operator expectations.

---

## Explicitly out of scope here

- Rewriting frozen `docs/archive/**`
- Re-opening closed historical gate findings as live harness work
- Harness markdown→JSON conversion (still a non-goal)
