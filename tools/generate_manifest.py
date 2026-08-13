#!/usr/bin/env python3
"""
Generate manifest.json for the BookReader self-hosted library.

Run this in the root of your GitHub books repo. It scans every .epub and
.pdf file (optionally inside subfolders) and writes manifest.json listing
each book with a stable id (relative path slug).

Usage:
    python3 tools/generate_manifest.py [--output manifest.json] [--dir books]
"""

import argparse
import json
import os
import re
import sys


def slugify(path: str) -> str:
    stem = re.sub(r"\.(epub|pdf)$", "", path, flags=re.IGNORECASE)
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return slug or "book"


def author_from_path(path: str) -> str:
    parts = os.path.normpath(path).split(os.sep)
    if len(parts) >= 2:
        return parts[0].replace("_", " ").replace("-", " ").title()
    return "Unknown"


def scan(root: str) -> list:
    books = []
    for dirpath, _, filenames in os.walk(root):
        for name in sorted(filenames):
            lower = name.lower()
            if not lower.endswith((".epub", ".pdf")):
                continue
            rel = os.path.join(os.path.relpath(dirpath, root), name)
            rel = rel.replace(os.sep, "/")
            if rel.startswith("./"):
                rel = rel[2:]
            full = os.path.join(dirpath, name)
            books.append(
                {
                    "id": slugify(rel),
                    "title": os.path.splitext(name)[0],
                    "author": author_from_path(rel),
                    "file": rel,
                    "size": os.path.getsize(full),
                }
            )
    return books


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate BookReader manifest.json")
    parser.add_argument("--dir", default="books", help="Directory to scan (default: books)")
    parser.add_argument("--output", default="manifest.json", help="Output file (default: manifest.json)")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"error: directory not found: {args.dir}", file=sys.stderr)
        return 1

    books = scan(args.dir)
    if not books:
        print(f"warning: no .epub/.pdf files found under {args.dir}", file=sys.stderr)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"books": books}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"wrote {args.output} with {len(books)} book(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
