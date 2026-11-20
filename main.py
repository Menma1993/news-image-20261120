#!/usr/bin/env python3
"""Entry point for news-image-20261120: copy the pre-rendered image out.

Stdlib only — no network, no third-party packages. The front page is
drawn at build time by draw.py (PIL, run locally) and shipped in this
repository as entry.png; this program only copies those exact bytes to
the output directory, so both grading runs write identical files.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    if not os.path.isfile(SRC):
        raise SystemExit("entry.png missing next to main.py: run draw.py first")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    if os.path.getsize(dst) != os.path.getsize(SRC):
        raise SystemExit("copy incomplete: size mismatch on " + dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main()
