"""Archive process must surface task.side_effects (flexibility step 8 / A5)."""

from __future__ import annotations

from pathlib import Path

FORMAT = ".cursor/skills/task-archive/archive-format.md"
SKILL = ".cursor/skills/task-archive/SKILL.md"
SHEEP = ".cursor/agents/sheep-archive.md"
NICKI = ".cursor/agents/nicki.md"

# Contract needles — archive drafts from these docs, so prose is the authority.
NEEDLES = (
    (FORMAT, "task.side_effects"),
    (FORMAT, "Ad-hoc <step> at <at>"),
    (FORMAT, "no artifact"),
    (FORMAT, "append one `process` row per"),
    (SKILL, "side_effects"),
    (SHEEP, "side_effects"),
    (NICKI, "--step <requested step>"),
    (NICKI, "--mode adhoc"),
)


def run(root: Path) -> None:
    failures: list[str] = []
    for rel, needle in NEEDLES:
        text = (root / rel).read_text(encoding="utf-8")
        if needle not in text:
            failures.append(f"fail: {rel} missing {needle!r}")

    if failures:
        raise AssertionError("\n".join(failures))
    print("smoke-archive-side-effects: ok")
