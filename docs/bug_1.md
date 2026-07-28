# check-gate.py bug: acceptance not appended to completed_steps

Date: 2026-07-28. Task: `project-jung/clinical-profile`
(`worktrees/project-jung-clinical-profile`).

## Summary

After the user explicitly accepted the task in chat, the status write updated
`task.current_step` to `"acceptance"` and `task.next_step` to `"sync"` in
`status.json`, but did **not** append `"acceptance"` to
`task.completed_steps` (which still ended at `review`). The subsequent gate
check for `sync` denied the transition: `check-gate.py` requires
`"acceptance"` to be present in `completed_steps`, not just in
`current_step`, so the gate read a task that — by its own bookkeeping — had
never completed acceptance.

## Reproduction

1. Complete `review` with a `ready_for_acceptance` / approved verdict.
2. User accepts the task directly in chat (Nicki-only checkpoint, no sheep
   dispatched).
3. Status write path (`sheep-status`, backed by `update-status.py`) runs —
   observe `status.json`: `current_step: "acceptance"`, `next_step: "sync"`,
   `completed_steps` unchanged, still ending at `review`.
4. Attempt the `sync` gate check via `check-gate.py`. Result:
   `"allowed": false`, `"sheep": null`, reason `"sync gate: acceptance not
   recorded and no override"`, `"user_confirm": "local commit, merge main
   into feature branch, push feature branch"`.

## Root cause

Hypothesis: the status-write path for Nicki-only steps (acceptance has no
sheep dispatch) only updates `current_step`/`next_step` and never appends to
`completed_steps`. Sheep-dispatched steps presumably append to
`completed_steps` correctly as part of their own write contract — acceptance,
having no sheep, falls through a gap in that shared write logic.

## Impact

The `sync` gate always denies immediately after acceptance unless overridden.
Any other downstream gate that checks `completed_steps` for `"acceptance"`
(e.g. `integrate`, `archive`, `close`) is likely affected the same way, since
they sit later in the pipeline than this same Nicki-only checkpoint.

## Workaround used

Re-ran `check-gate.py` for `sync` with `--user-confirmed --override`, which
the harness reserves for exactly this kind of situation.

## Suggested fix

Make the acceptance-recording status write append `"acceptance"` to
`completed_steps`, consistent with how sheep-dispatched steps record
completion. Add a regression fixture for this case — "acceptance recorded
but `completed_steps` not updated" is a good candidate for the smoke-fixture
matrix tracked in `docs/tasks.md` item #10 (fixtures exercised through
`check-gate.py`).
