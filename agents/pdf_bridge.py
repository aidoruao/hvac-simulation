#!/usr/bin/env python3
"""
pdf_bridge.py — Extract structured sections from design spec PDFs.

Godot-native AI calls this to read papers and apply their architecture
to viewport verification, mutation planning, and self-audit.

Usage:
    python3 agents/pdf_bridge.py <pdf> --section "3.1 Hybrid Vision Encoder"
"""
import sys
import json
import re
import argparse
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    print(json.dumps({"error": "PyMuPDF not installed. Run: pip install PyMuPDF"}))
    sys.exit(1)


def extract_section(pdf_path: str, section_title: str) -> Optional[str]:
    """Extract text from a section by title pattern (e.g., '3.1 Hybrid Vision Encoder')."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    # Match the section heading and capture text until next numbered section or EOF
    pattern = rf"({re.escape(section_title)}.*?)(?=\n\d+\.\d+\s|\n\d+\s[A-Z]|\Z)"
    match = re.search(pattern, full_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_all_sections(pdf_path: str) -> list:
    """Return all detected section headings and their page ranges."""
    doc = fitz.open(pdf_path)
    sections = []
    for i, page in enumerate(doc):
        text = page.get_text()
        # Find section headings like "3.1 Something" or "4 Method"
        for m in re.finditer(r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z\s\-]+)", text, re.MULTILINE):
            sections.append({
                "number": m.group(1),
                "title": m.group(2).strip(),
                "page": i + 1,
            })
    doc.close()
    return sections


def extract_metadata(pdf_path: str) -> dict:
    """Return PDF metadata: title, author, page count."""
    doc = fitz.open(pdf_path)
    meta = doc.metadata
    return {
        "title": meta.get("title", "unknown"),
        "author": meta.get("author", "unknown"),
        "pages": len(doc),
        "format": meta.get("format", "PDF"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract structured sections from design spec PDFs."
    )
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--section", help="Section title or number to extract")
    parser.add_argument("--list", action="store_true", help="List all detected sections")
    parser.add_argument("--meta", action="store_true", help="Show PDF metadata")
    args = parser.parse_args()

    if args.meta:
        print(json.dumps(extract_metadata(args.pdf), indent=2))
        return 0

    if args.list:
        sections = extract_all_sections(args.pdf)
        print(json.dumps(sections, indent=2))
        return 0

    if args.section:
        text = extract_section(args.pdf, args.section)
        result = {
            "section": args.section,
            "found": text is not None,
            "text": text[:3000] if text else None,
        }
        print(json.dumps(result, indent=2))
        return 0 if text else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
