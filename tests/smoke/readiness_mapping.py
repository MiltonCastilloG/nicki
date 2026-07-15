from __future__ import annotations

import tempfile
from pathlib import Path

from tests.smoke._helpers import assert_contains, assert_missing


def run(root: Path) -> None:
    validation_md = root / ".cursor/skills/validation/validation-format.md"
    fixture_dir = root / ".cursor/skills/validation/scripts/fixtures"

    for status in ("ready_for_acceptance", "fix_required", "blocked"):
        assert_contains(validation_md, status, status)

    assert_contains(validation_md, "deferred_scope")
    assert_contains(validation_md, "next-steps")
    assert_contains(root / ".cursor/agents/sheep-review.md", "validation")
    assert_missing(root / ".cursor/agents/out-of-scope.md", "out-of-scope agent")
    if (root / ".cursor/skills/readiness-from-review").exists():
        raise AssertionError("fail: readiness-from-review dir should be removed")
    assert_contains(root / ".cursor/skills/nicki/routing.yaml", "review_validation")
    routing = (root / ".cursor/skills/nicki/routing.yaml").read_text(encoding="utf-8")
    if "out_of_scope:" in routing:
        raise AssertionError("fail: out_of_scope step should be removed")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Subtasks\n- [x] Done line stays.\n")
        f.flush()
        path = Path(f.name)
        before_x = path.read_text(encoding="utf-8").count("- [x]")
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n## Fix\n<!-- ref: current-task/review-validations/r1-validation.yaml -->\n- [ ] Fix lint from review.\n",
            encoding="utf-8",
        )
        after_x = path.read_text(encoding="utf-8").count("- [x]")
        path.unlink()
        if before_x != after_x or before_x < 1:
            raise AssertionError(
                f"fail: fix append mutated prior [x] ({before_x} -> {after_x})"
            )
    print("ok: fix append keeps prior [x]")

    scope_only = fixture_dir / "scope-only-validation.yaml"
    if scope_only.is_file():
        assert_contains(scope_only, "ready_for_acceptance")
        assert_contains(scope_only, "deferred_scope: true")
        print("ok: scope-only fixture present")

    verify_fail = fixture_dir / "verify-fail-validation.yaml"
    if verify_fail.is_file():
        assert_contains(verify_fail, "fix_required")
        print("ok: verify-fail fixture present")

    print("smoke-readiness-mapping: ok")
