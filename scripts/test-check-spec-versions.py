#!/usr/bin/env python3
"""Edge-case suite for check-spec-versions.py, against real temporary git repos."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / "check-spec-versions.py"

SPEC = "# Indexer v4 Specification\n\n**Latest Draft:** spec {v}\n\n## Abstract\n\n{body}\n"


def spec(v, body="text"):
    return SPEC.format(v=v, body=body)


class Repo:
    def __init__(self, files):
        self.dir = Path(tempfile.mkdtemp())
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@t.t")
        self.git("config", "user.name", "t")
        self.write(files)
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.git("branch", "-f", "origin/main", "main")

    def git(self, *a):
        return subprocess.run(
            ("git", *a), cwd=self.dir, capture_output=True, text=True, check=False
        )

    def write(self, files):
        for path, content in files.items():
            p = self.dir / path
            if content is None:
                p.unlink(missing_ok=True)
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    def branch(self, files, commit=True):
        self.git("checkout", "-q", "-b", "pr")
        self.write(files)
        if commit:
            self.git("add", "-A")
            self.git("commit", "-qm", "pr")

    def advance_main(self, files):
        """Simulate a competing PR landing on main after this branch was cut."""
        cur = self.git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        self.git("checkout", "-q", "main")
        self.write(files)
        self.git("add", "-A")
        self.git("commit", "-qm", "competing")
        self.git("branch", "-f", "origin/main", "main")
        self.git("checkout", "-q", cur)

    def run(self, *args):
        r = subprocess.run(
            (sys.executable, str(CHECK), *args),
            cwd=self.dir,
            capture_output=True,
            text=True,
        )
        return r.returncode, r.stdout + r.stderr

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class Case(unittest.TestCase):
    def setUp(self):
        self.repos = []

    def tearDown(self):
        for r in self.repos:
            r.cleanup()

    def repo(self, files):
        r = Repo(files)
        self.repos.append(r)
        return r

    def check(self, base_files, pr_files, competing=None, args=("--base", "origin/main")):
        r = self.repo(base_files)
        r.branch(pr_files)
        if competing:
            r.advance_main(competing)
        return r.run(*args)

    # ---- core rule ----

    def test_bump_passes(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7")},
            {"v4/idx/spec.md": spec("v4-draft8", "new")},
        )
        self.assertEqual(rc, 0, out)
        self.assertIn("v4-draft7 → v4-draft8", out)

    def test_forgotten_bump_fails(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7")},
            {"v4/idx/spec.md": spec("v4-draft7", "changed prose")},
        )
        self.assertEqual(rc, 1, out)
        self.assertIn("v4-draft8 or later", out)

    def test_identical_edit_collision_fails(self):
        """Two PRs both bump draft3 -> draft4; the second must not slip through."""
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft3")},
            {"v4/idx/spec.md": spec("v4-draft4", "mine")},
            competing={"v4/idx/spec.md": spec("v4-draft4", "theirs")},
        )
        self.assertEqual(rc, 1, out)
        self.assertIn("v4-draft5 or later", out)

    def test_decrement_fails(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7")},
            {"v4/idx/spec.md": spec("v4-draft6", "x")},
        )
        self.assertEqual(rc, 1, out)

    def test_numeric_not_lexical_ordering(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft9")},
            {"v4/idx/spec.md": spec("v4-draft10", "x")},
        )
        self.assertEqual(rc, 0, out)

    # ---- lifecycle transitions the sibling repos actually perform ----

    def test_draft_to_rc(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft16")},
            {"v4/idx/spec.md": spec("v4-rc1", "x")},
        )
        self.assertEqual(rc, 0, out)

    def test_rc_to_stable(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-rc5")},
            {"v4/idx/spec.md": spec("v4", "x")},
        )
        self.assertEqual(rc, 0, out)

    def test_stable_to_next_major(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4")},
            {"v4/idx/spec.md": spec("v5-draft0", "x")},
        )
        self.assertEqual(rc, 0, out)

    def test_rc_back_to_draft_fails(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-rc1")},
            {"v4/idx/spec.md": spec("v4-draft17", "x")},
        )
        self.assertEqual(rc, 1, out)

    # ---- what obliges a bump ----

    def test_schema_only_change_obliges_bump(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7"), "v4/idx/schemas/a.json": "{}"},
            {"v4/idx/schemas/a.json": '{"a":1}'},
        )
        self.assertEqual(rc, 1, out)
        self.assertIn("schemas/a.json", out)

    def test_ungoverned_file_needs_nothing(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7"), "README.md": "hi"},
            {"README.md": "hello"},
        )
        self.assertEqual(rc, 0, out)
        self.assertIn("no governed spec changed", out)

    def test_exempt_spec_needs_nothing(self):
        rc, out = self.check(
            {
                "v4/idx/spec.md": spec("v4-draft7"),
                "playground/spec.md": "# P\n\n**Status:** DRAFT 0.2\n",
            },
            {"playground/spec.md": "# P\n\n**Status:** DRAFT 0.2 edited\n"},
        )
        self.assertEqual(rc, 0, out)

    def test_new_spec_passes(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7")},
            {"v4/new/spec.md": spec("v4-draft1")},
        )
        self.assertEqual(rc, 0, out)
        self.assertIn("new spec at v4-draft1", out)

    def test_deleted_spec_passes(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7"), "v4/old/spec.md": spec("v4-draft2")},
            {"v4/old/spec.md": None},
        )
        self.assertEqual(rc, 0, out)

    def test_deepest_root_wins(self):
        rc, out = self.check(
            {
                "v4/idx/spec.md": spec("v4-draft7"),
                "v4/idx/sub/spec.md": spec("v4-draft1"),
            },
            {"v4/idx/sub/spec.md": spec("v4-draft2", "x")},
        )
        self.assertEqual(rc, 0, out)
        self.assertNotIn("✗", out)

    # ---- the guard ----

    def test_new_markerless_spec_fails(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7")},
            {"v4/thing/spec.md": "# Thing\n\n**Status:** DRAFT\n"},
        )
        self.assertEqual(rc, 1, out)
        self.assertIn("no '**Latest Draft:**", out)

    def test_removing_a_marker_fails(self):
        rc, out = self.check(
            {"v4/idx/spec.md": spec("v4-draft7")},
            {"v4/idx/spec.md": "# Indexer\n\n## Abstract\n\ntext\n"},
        )
        self.assertEqual(rc, 1, out)

    # ---- parsing ----

    def test_linked_lowercase_marker_form(self):
        linked = (
            "# VT v5 Specification\n\n"
            "**Latest draft:** [spec v5-draft0](https://x/)\n\n## Abstract\n\nbody\n"
        )
        linked2 = linked.replace("v5-draft0", "v5-draft1").replace("body", "new")
        rc, out = self.check({"v4/idx/spec.md": linked}, {"v4/idx/spec.md": linked2})
        self.assertEqual(rc, 0, out)
        self.assertIn("v5-draft0 → v5-draft1", out)

    def test_marker_in_prose_is_not_picked_up(self):
        tricky = (
            "# Indexer\n\n**Latest Draft:** spec v4-draft7\n\n## Abstract\n\n"
            "Historically the **Latest Draft:** spec v9-draft9 was cited here.\n"
        )
        rc, out = self.check(
            {"v4/idx/spec.md": tricky},
            {"v4/idx/spec.md": tricky.replace("Historically", "Formerly")},
        )
        self.assertEqual(rc, 1, out)
        self.assertIn("v4-draft8 or later", out)

    # ---- local usage (working tree, uncommitted) ----

    def test_uncommitted_changes_are_checked(self):
        r = self.repo({"v4/idx/spec.md": spec("v4-draft7")})
        r.branch({"v4/idx/spec.md": spec("v4-draft7", "edited")}, commit=False)
        rc, out = r.run("--base", "origin/main")
        self.assertEqual(rc, 1, out)
        self.assertIn("v4-draft8 or later", out)

    # ---- known limitation, documented so a port does not trip over it ----

    def test_root_spec_governs_whole_repo(self):
        """A spec.md at the repo root owns every path, including .github/.

        Does not apply here (no root spec.md), but verifiable-trust-spec has
        one, so a port there needs an ignore list.
        """
        rc, out = self.check(
            {"spec.md": spec("v4-draft7"), ".github/workflows/w.yml": "on: push"},
            {".github/workflows/w.yml": "on: pull_request"},
        )
        self.assertEqual(rc, 1, out)
        self.assertIn(".github/workflows/w.yml", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
