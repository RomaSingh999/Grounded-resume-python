"""Fact-check helper: run this before you publish.

    python factcheck.py                      # lists every claim and every TODO
    python factcheck.py --pdf resume.pdf     # also checks claims against your resume PDF

It never edits anything. You read the report and fix resume.json yourself.
"""
import argparse
import re
import subprocess
import sys

from grounded import build_facts, is_todo, load_resume


def pdf_text(path: str) -> str:
    try:
        from pypdf import PdfReader
        return " ".join((p.extract_text() or "") for p in PdfReader(path).pages)
    except ImportError:
        pass
    try:
        return subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, check=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit("Install pypdf (pip install pypdf) or poppler-utils to read the PDF.")


def key_terms(text: str) -> list[str]:
    """Numbers, capitalised names and tech words are what must match the source."""
    terms = re.findall(r"\d[\d,.%]*|[A-Z][A-Za-z0-9+#.]{2,}", text)
    return [t for t in terms if t.lower() not in {"roma", "she", "the"}]


def walk_todos(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_todos(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_todos(v, f"{path}[{i}]")
    elif is_todo(node):
        yield path, node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", help="path to your resume PDF")
    args = ap.parse_args()

    resume = load_resume()
    facts = build_facts(resume)
    source = pdf_text(args.pdf).lower() if args.pdf else None

    print(f"== {len(facts)} claims the site and chat can make ==\n")
    unmatched = 0
    for f in facts:
        line = f"[{f['section']}] {f['text']}"
        if source is not None:
            missing = [t for t in key_terms(f["text"]) if t.lower() not in source]
            if missing:
                unmatched += 1
                line += f"\n    NOT FOUND IN PDF: {', '.join(missing)}"
        print(line)

    todos = list(walk_todos(resume))
    print(f"\n== {len(todos)} TODO items (hidden from the site until you fill them) ==")
    for path, val in todos:
        print(f"  {path}: {val}")

    if source is not None:
        print(f"\n{unmatched} claim(s) contain terms missing from the PDF. Check each one by hand.")
    print("\nBefore publishing: read every claim above and confirm it is true and provable.")


if __name__ == "__main__":
    main()
