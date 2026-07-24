#!/usr/bin/env python3
"""
pdf_bridge.py — Extract structured sections from design spec PDFs.

Godot-native AI calls this to read papers and apply their architecture
to viewport verification, mutation planning, and self-audit.

Fixed: matches section content on the correct page, not TOC entries.

Usage:
    python3 agents/pdf_bridge.py <pdf> --section "3.1"
"""
import sys
import json
import re
import argparse
from typing import Optional, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print(json.dumps({"error": "PyMuPDF not installed. Run: pip install PyMuPDF"}))
    sys.exit(1)


def extract_section_content(pdf_path: str, section_number: str) -> Optional[Dict[str, Any]]:
    """
    Extract a numbered section from page content, skipping TOC pages.
    Searches each page for a section header like '3.1  Architecture'
    and captures text until the next numbered section.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # Skip early pages that are TOC (heuristic: first 15% of pages)
    start_page = max(1, int(total_pages * 0.1))

    for page_num in range(start_page, total_pages):
        page = doc[page_num]
        text = page.get_text()

        # Match section header: optional newline, number, spaces, title (3-80 chars), newline
        pattern = (
            r"(?:^|\n)"
            + re.escape(section_number)
            + r"[\.\s]+([^\n]{3,80})\n"
            + r"(.*?)(?=\n\d+(?:\.\d+)*\s+[A-Z]|\Z)"
        )
        match = re.search(pattern, text, re.DOTALL)
        if match:
            title = match.group(1).strip()
            content = match.group(2).strip()
            # Only return if we found substantial content (not just a page number)
            if len(content) > 50:
                doc.close()
                return {
                    "section_number": section_number,
                    "title": title,
                    "content": content[:5000],
                    "page": page_num + 1,  # 1-indexed
                    "found": True,
                }

    doc.close()
    return None


def extract_metadata(pdf_path: str) -> dict:
    """Return PDF metadata: title, author, page count."""
    doc = fitz.open(pdf_path)
    meta = doc.metadata
    pages = len(doc)
    doc.close()
    return {
        "title": meta.get("title", "unknown"),
        "author": meta.get("author", "unknown"),
        "pages": pages,
        "format": meta.get("format", "PDF"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract structured sections from design spec PDFs."
    )
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--section", help="Section number to extract (e.g., '3.1')")
    parser.add_argument("--meta", action="store_true", help="Show PDF metadata")
    args = parser.parse_args()

    if args.meta:
        print(json.dumps(extract_metadata(args.pdf), indent=2))
        return 0

    if args.section:
        result = extract_section_content(args.pdf, args.section)
        if result:
            print(json.dumps(result, indent=2))
            return 0
        else:
            print(json.dumps({
                "section": args.section,
                "found": False,
                "error": "Section not found in page content (skipped TOC pages)"
            }, indent=2))
            return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
