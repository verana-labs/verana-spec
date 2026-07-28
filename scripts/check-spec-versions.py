#!/usr/bin/env python3
"""Fail if a changed spec's draft version was not bumped.

A spec root is any directory whose spec.md carries a marker line, e.g.

    **Latest Draft:** spec v4-draft7

Any change under a spec root requires that spec's version to be strictly
greater than the version on the base branch.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# spec.md files allowed to carry no marker. Delete an entry the day that spec
# adopts the convention; it is then governed like any other.
MARKERLESS_OK = {
    "v3/verana-frontend/spec.md": "v3, historical",
    "v4/verana-frontend/spec.md": "Pre-Draft, drafting not started",
    "v4/vt-flow-protocol/spec.md": "carries its own protocol version (1.0)",
    "playground/spec.md": "playground/ is unversioned (DRAFT 0.x + date)",
    "playground/verana-explained/spec.md": "playground/ is unversioned",
}

MARKER = re.compile(
    r"^[ \t]*[-*]?[ \t]*\*\*Latest[ \t]+[Dd]raft:?\*\*[ \t]*\[?[ \t]*spec[ \t]+"
    r"(v\d+(?:-(?:draft|rc)\d+)?)\b"
)
VERSION = re.compile(r"^v(\d+)(?:-(draft|rc)(\d+))?$")
STAGE = {"draft": 0, "rc": 1}


def header(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return out


def marker(text: str | None) -> tuple[str | None, int]:
    """(version, 1-based line) of the marker in the header block."""
    if text is None:
        return None, 0
    for i, line in enumerate(header(text), 1):
        m = MARKER.match(line)
        if m:
            return m.group(1), i
    return None, 0


def key(version: str) -> tuple[int, int, int] | None:
    m = VERSION.match(version)
    if not m:
        return None
    major, stage, n = m.groups()
    return (int(major), 2, 0) if stage is None else (int(major), STAGE[stage], int(n))


def bumped(version: str) -> str:
    major, stage, n = key(version)
    if stage == 2:
        return f"v{major + 1}-draft0"
    return f"v{major}-{'draft' if stage == 0 else 'rc'}{n + 1}"


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(("git", *args), capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


class Tree:
    """Reads repo files from a git ref, or from the working tree when ref is None."""

    def __init__(self, ref: str | None):
        self.ref = ref

    def read(self, path: str) -> str | None:
        if self.ref is None:
            p = Path(path)
            return p.read_text(encoding="utf-8") if p.is_file() else None
        r = subprocess.run(
            ("git", "show", f"{self.ref}:{path}"), capture_output=True, text=True
        )
        return r.stdout if r.returncode == 0 else None

    def specs(self) -> list[str]:
        listing = (
            git("ls-files") if self.ref is None
            else git("ls-tree", "-r", "--name-only", self.ref)
        )
        return sorted(p for p in listing.splitlines() if Path(p).name == "spec.md")


def owner(path: str, roots: dict[str, str]) -> str | None:
    hits = [r for r in roots if r == "" or path.startswith(f"{r}/")]
    return max(hits, key=len) if hits else None


def annotate(path: str, line: int, message: str) -> None:
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error file={path},line={line}::{message}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="origin/main", help="base ref (default origin/main)")
    ap.add_argument("--head", help="head ref (default: working tree)")
    args = ap.parse_args()

    head = Tree(args.head)
    base = Tree(args.base)

    merge_base = git("merge-base", args.base, args.head or "HEAD").strip()
    diff = ("diff", "--name-only", merge_base) + ((args.head,) if args.head else ())
    changed = [p for p in git(*diff).splitlines() if p]

    roots: dict[str, str] = {}
    problems: list[str] = []

    for spec in head.specs():
        version, line = marker(head.read(spec))
        if version:
            roots[spec[: spec.rfind("/")] if "/" in spec else ""] = spec
        elif spec not in MARKERLESS_OK:
            problems.append(
                f"  ✗ {spec}\n"
                f"      no '**Latest Draft:** spec vN-draftM' marker, and not in MARKERLESS_OK"
            )
            annotate(spec, 1, "no Latest Draft marker (add one, or list it in MARKERLESS_OK)")

    obliged: dict[str, list[str]] = {}
    for path in changed:
        root = owner(path, roots)
        if root is not None:
            obliged.setdefault(root, []).append(path)

    passes: list[str] = []
    for root in sorted(obliged):
        spec = roots[root]
        files = obliged[root]
        head_v, line = marker(head.read(spec))
        base_v, _ = marker(base.read(spec))

        if base_v is None:
            passes.append(f"  ✓ {spec}   new spec at {head_v}")
        elif key(head_v) > key(base_v):
            passes.append(f"  ✓ {spec}   {base_v} → {head_v}")
        else:
            shown = ", ".join(files[:4])
            if len(files) > 4:
                shown += f", and {len(files) - 4} more"
            need = bumped(base_v)
            problems.append(
                f"  ✗ {spec}\n"
                f"      changed:  {shown}\n"
                f"      on {args.base}:  {base_v}\n"
                f"      this branch:    {head_v}\n"
                f"      needed:         {need} or later"
            )
            annotate(spec, line or 1, f"{args.base} is at {base_v}; bump this to {need}")

    print("spec draft-version check")
    print()
    for line_out in passes:
        print(line_out)
    for line_out in problems:
        print(line_out)
    if not passes and not problems:
        print("  no governed spec changed")
    print()

    if problems:
        n = len(problems)
        print(f"{n} problem{'s' if n > 1 else ''}.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
