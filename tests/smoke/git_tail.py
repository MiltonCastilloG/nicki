from __future__ import annotations

from pathlib import Path

from tests.smoke._helpers import assert_contains, assert_missing


def run(root: Path) -> None:
    failures: list[str] = []

    def check_exists(rel: str) -> None:
        path = root / rel
        if not path.exists():
            failures.append(f"fail: missing {rel}")
        else:
            print(f"ok: {rel}")

    for rel in (
        ".cursor/agents/sheep-sync.md",
        ".cursor/skills/sync-task/SKILL.md",
        ".cursor/agents/sheep-integrate.md",
        ".cursor/skills/integrate-task/SKILL.md",
    ):
        check_exists(rel)

    for rel in (
        ".cursor/agents/commit-task.md",
        ".cursor/agents/push-task.md",
        ".cursor/agents/merge-task.md",
        ".cursor/agents/publish-task.md",
    ):
        if (root / rel).exists():
            failures.append(f"fail: {rel} should be removed")

    try:
        assert_contains(
            root / ".cursor/skills/current-task-update/status-format.md", "| `sync`"
        )
        assert_contains(
            root / ".cursor/skills/current-task-update/status-format.md", "| `integrate`"
        )
        assert_contains(root / ".cursor/skills/close-task/SKILL.md", "Tail gate")
        assert_contains(root / ".cursor/agents/nicki.md", "sheep-integrate")
        assert_contains(root / ".cursor/skills/nicki/routing.yaml", "sheep-sync")
        assert_contains(
            root / ".cursor/skills/start-task/scripts/start-worktrees.sh", "PROJECT"
        )
        assert_contains(root / "README.md", "projects/")
        assert_contains(root / ".cursor/skills/sync-task/sync-format.md", "syncs/")
        assert_contains(
            root / ".cursor/skills/integrate-task/integrate-format.md", "integrates/"
        )
    except AssertionError as e:
        failures.append(str(e))

    if failures:
        raise AssertionError("\n".join(failures))

    print("smoke-git-tail: ok")
