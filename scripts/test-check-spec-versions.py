#!/usr/bin/env python3
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK = Path(__file__).resolve().parent / "check-spec-versions.py"


def load():
    found = importlib.util.spec_from_file_location("check", CHECK)
    module = importlib.util.module_from_spec(found)
    found.loader.exec_module(module)
    return module


def spec(version, body="text"):
    return f"# Spec\n\n**Latest Draft:** spec {version}\n\n## Abstract\n\n{body}\n"


def linked(version, body="text"):
    return f"# Spec\n\n**Latest draft:** [spec {version}](https://x/)\n\n## Abstract\n\n{body}\n"


def prose(body):
    return (
        "# Spec\n\n**Latest Draft:** spec v4-draft7\n\n## Abstract\n\n"
        f"Once cited as **Latest Draft:** spec v9-draft9. {body}\n"
    )


ORDER = [
    ("v4-draft7", "v4-draft8", 0),
    ("v4-draft9", "v4-draft10", 0),
    ("v4-draft16", "v4-rc1", 0),
    ("v4-rc5", "v4", 0),
    ("v4", "v5-draft0", 0),
    ("v4-draft7", "v4-draft7", 1),
    ("v4-draft7", "v4-draft6", 1),
    ("v4-rc1", "v4-draft17", 1),
]

MARKERS = [
    ("**Latest Draft:** spec v4-draft7", "v4-draft7"),
    ("**Latest draft:** [spec v5-draft0](https://x/)", "v5-draft0"),
    ("- **Latest Draft:** spec v4-rc2", "v4-rc2"),
    ("**Latest Draft:** spec v4", "v4"),
    ("**Latest Draft:**spec v4-draft7", "v4-draft7"),
    ("**Latest Draft:** v4-draft8", "v4-draft8"),
    ("**Latest Draft:** spec v4-draft7 (2026-07-16)", "v4-draft7"),
    ("**Latest Draft:** spec\u00a0v4-draft7", "v4-draft7"),
    ("**Latest Draft:** spec v4-draft7   ", "v4-draft7"),
    ("**Specification Status:** Pre-Draft", None),
    ("- **Status:** DRAFT", None),
    ("**Status:** DRAFT 0.2 (rebuilt)", None),
]

SCENARIOS = [
    ("branch behind main",
     {"a/spec.md": spec("v4-draft5")},
     {"a/spec.md": spec("v4-draft6", "mine")},
     {"a/spec.md": spec("v4-draft7", "theirs")}, 1, "v4-draft8 or later"),

    ("schema change obliges a bump",
     {"a/spec.md": spec("v4-draft7"), "a/s.json": "{}"},
     {"a/s.json": '{"x": 1}'}, None, 1, "s.json"),

    ("ungoverned file obliges nothing",
     {"a/spec.md": spec("v4-draft7"), "README.md": "hi"},
     {"README.md": "hello"}, None, 0, "no governed spec changed"),

    ("markerless spec obliges nothing",
     {"a/spec.md": spec("v4-draft7"), "playground/spec.md": "# P\n\n**Status:** DRAFT 0.2\n"},
     {"playground/spec.md": "# P\n\n**Status:** DRAFT 0.3\n"}, None, 0, None),

    ("new spec passes",
     {"a/spec.md": spec("v4-draft7")},
     {"b/spec.md": spec("v4-draft1")}, None, 0, "new spec at v4-draft1"),

    ("deleted spec passes",
     {"a/spec.md": spec("v4-draft7"), "b/spec.md": spec("v4-draft2")},
     {"b/spec.md": None}, None, 0, None),

    ("deepest root wins",
     {"a/spec.md": spec("v4-draft7"), "a/b/spec.md": spec("v4-draft1")},
     {"a/b/spec.md": spec("v4-draft2", "x")}, None, 0, None),

    ("identical edit by two PRs",
     {"a/spec.md": spec("v4-draft3")},
     {"a/spec.md": spec("v4-draft4", "mine")},
     {"a/spec.md": spec("v4-draft4", "theirs")}, 1, "v4-draft5 or later"),

    ("new markerless spec fails",
     {"a/spec.md": spec("v4-draft7")},
     {"b/spec.md": "# B\n\n**Status:** DRAFT\n"}, None, 1, "no '**Latest Draft:**"),

    ("removing a marker fails",
     {"a/spec.md": spec("v4-draft7")},
     {"a/spec.md": "# Spec\n\n## Abstract\n\ntext\n"}, None, 1, None),

    ("linked lowercase marker",
     {"a/spec.md": linked("v5-draft0")},
     {"a/spec.md": linked("v5-draft1", "new")}, None, 0, "v5-draft0 -> v5-draft1"),

    ("marker in prose is ignored",
     {"a/spec.md": prose("one")},
     {"a/spec.md": prose("two")}, None, 1, "v4-draft8 or later"),

    ("root spec governs the whole repo",
     {"spec.md": spec("v4-draft7"), ".github/w.yml": "on: push"},
     {".github/w.yml": "on: pull_request"}, None, 1, ".github/w.yml"),
]


def write(root, files):
    for name, content in files.items():
        path = root / name
        if content is None:
            path.unlink(missing_ok=True)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run(base_files, head_files, competing=None, commit=True):
    root = Path(tempfile.mkdtemp())

    def git(*args):
        return subprocess.run(("git", *args), cwd=root, capture_output=True, text=True)

    try:
        git("init", "-q", "-b", "main")
        git("config", "user.email", "t@t.t")
        git("config", "user.name", "t")
        write(root, base_files)
        git("add", "-A")
        git("commit", "-qm", "base")
        git("branch", "origin/main", "main")

        git("checkout", "-q", "-b", "pr")
        write(root, head_files)
        if commit:
            git("add", "-A")
            git("commit", "-qm", "pr")

        if competing:
            git("checkout", "-q", "main")
            write(root, competing)
            git("add", "-A")
            git("commit", "-qm", "competing")
            git("branch", "-f", "origin/main", "main")
            git("checkout", "-q", "pr")

        done = subprocess.run(
            (sys.executable, str(CHECK)), cwd=root, capture_output=True, text=True
        )
        return done.returncode, done.stdout + done.stderr
    finally:
        shutil.rmtree(root, ignore_errors=True)


class Check(unittest.TestCase):
    def test_ordering(self):
        for was, now, want in ORDER:
            with self.subTest(f"{was} -> {now}"):
                code, out = run({"a/spec.md": spec(was)}, {"a/spec.md": spec(now, "x")})
                self.assertEqual(code, want, out)

    def test_scenarios(self):
        for name, base, head, competing, want, text in SCENARIOS:
            with self.subTest(name):
                code, out = run(base, head, competing)
                self.assertEqual(code, want, out)
                if text:
                    self.assertIn(text, out)

    def test_marker_forms(self):
        check = load()
        for line, want in MARKERS:
            with self.subTest(line):
                got, _, _ = check.marker(f"# T\n\n{line}\n\n## A\n")
                self.assertEqual(got, want)

    def test_crlf_document(self):
        check = load()
        got, _, _ = check.marker(
            "# T\r\n\r\n**Latest Draft:** spec v4-draft7\r\n\r\n## A\r\n"
        )
        self.assertEqual(got, "v4-draft7")

    def test_uncommitted_changes_are_checked(self):
        code, out = run(
            {"a/spec.md": spec("v4-draft7")},
            {"a/spec.md": spec("v4-draft7", "edited")},
            commit=False,
        )
        self.assertEqual(code, 1, out)
        self.assertIn("v4-draft8 or later", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
