#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path

MARKERLESS_OK = {
    "v3/verana-frontend/spec.md",
    "v4/verana-frontend/spec.md",
    "v4/vt-flow-protocol/spec.md",
    "playground/spec.md",
    "playground/verana-explained/spec.md",
}

MARKER = re.compile(
    r"^[^\S\n]*[-*]?[^\S\n]*\*\*Latest[^\S\n]+[Dd]raft:?\*\*[^\S\n]*\[?[^\S\n]*"
    r"(?:spec[^\S\n]+)?(v(\d+)(?:-(draft|rc)(\d+))?)\b"
)
STAGE = {"draft": 0, "rc": 1}


def git(*args, required=True):
    p = subprocess.run(("git", *args), capture_output=True, text=True)
    if p.returncode:
        if required:
            sys.exit(f"git {' '.join(args)}: {p.stderr.strip()}")
        return None
    return p.stdout


def marker(text):
    for number, line in enumerate((text or "").splitlines(), 1):
        if line.startswith("## "):
            break
        found = MARKER.match(line)
        if found:
            name, major, stage, seq = found.groups()
            rank = (int(major), STAGE[stage], int(seq)) if stage else (int(major), 2, 0)
            return name, rank, number
    return None, None, 0


def bumped(rank):
    major, stage, seq = rank
    if stage == 2:
        return f"v{major + 1}-draft0"
    return f"v{major}-{'draft' if stage == 0 else 'rc'}{seq + 1}"


def annotate(path, line, message):
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error file={path},line={line}::{message}")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    merge_base = git("merge-base", base, "HEAD").strip()
    changed = git("diff", "--name-only", merge_base).splitlines()

    roots, passes, problems = {}, [], []

    for path in git("ls-files").splitlines():
        if Path(path).name != "spec.md" or not Path(path).is_file():
            continue
        name, rank, line = marker(Path(path).read_text(encoding="utf-8"))
        if rank:
            roots[path.rpartition("/")[0]] = (path, name, rank, line)
        elif path not in MARKERLESS_OK:
            problems.append(f"  ✗ {path}\n      no '**Latest Draft:** spec vN-draftM' marker")
            annotate(path, 1, "no Latest Draft marker; add one or list it in MARKERLESS_OK")

    owed = {}
    for path in changed:
        under = [root for root in roots if root == "" or path.startswith(f"{root}/")]
        if under:
            owed.setdefault(max(under, key=len), []).append(path)

    for root in sorted(owed):
        spec, name, rank, line = roots[root]
        was, was_rank, _ = marker(git("show", f"{base}:{spec}", required=False))
        if was_rank is None:
            passes.append(f"  ✓ {spec}   new spec at {name}")
        elif rank > was_rank:
            passes.append(f"  ✓ {spec}   {was} -> {name}")
        else:
            files = owed[root]
            shown = ", ".join(files[:3])
            if len(files) > 3:
                shown += f", and {len(files) - 3} more"
            need = bumped(was_rank)
            problems.append(
                f"  ✗ {spec}\n"
                f"      changed:  {shown}\n"
                f"      {base}:  {was}\n"
                f"      here:     {name}\n"
                f"      needed:   {need} or later"
            )
            annotate(spec, line, f"{base} is at {was}; bump this to {need}")

    print("spec draft-version check\n")
    for text in passes + problems:
        print(text)
    if not passes and not problems:
        print("  no governed spec changed")

    if problems:
        print(f"\n{len(problems)} problem{'s' if len(problems) > 1 else ''}.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
