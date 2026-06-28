"""
retro_qc.py - Generate QC reports for existing blog articles created before the QC system.

Scans sites/site-01/frontend/src/routes/blog.*.tsx files, extracts article content,
runs the same quality checks as content_factory.py's stage4_qc, and saves reports to docs/.

Usage:
    python tools/retro_qc.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
DOCS_DIR = ROOT / "docs"

# --- QC logic copied from tools/content_factory.py stage4_qc ---

AI_PHRASES = [
    "Furthermore", "Moreover", "In conclusion",
    "It's important to note", "It is worth noting",
    "Delve", "Tapestry", "Leverage", "Embark",
]

HUMAN_MARKERS = [
    "here's the thing", "honestly", "i've tested",
    "i've found", "in my testing", "look,", "that's it",
    "who cares", "the thing is", "let me break",
    "the bottom line", "i have seen", "that said", "the truth is",
    "i have found", "in my testing", "let me break this down",
    "here is the thing", "i have tested", "who cares",
]


def extract_content(tsx_text: str) -> tuple[str, int]:
    """Extract plain text and h2 count from the prose div in a TSX blog file.

    Returns (plain_text, h2_count). The h2 count is derived from <h2> tags
    in the raw TSX before stripping, since the stage4_qc markdown regex
    (``^##\\s``) won't match after tags are removed.
    """
    match = re.search(
        r'<div\s+className="prose\s+prose-gray\s+prose-lg\s+max-w-none">',
        tsx_text,
    )
    if not match:
        return "", 0

    # Take everything from the prose div opening to end of file
    raw = tsx_text[match.start():]

    # Count <h2> tags in the raw TSX (matches stage4_qc h2_count logic)
    h2_count = len(re.findall(r"<h2[\s>]", raw))

    # Strip all JSX tags to get plain text
    text = re.sub(r"<[^>]+>", " ", raw)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text, h2_count


def extract_keyword(tsx_text: str) -> str:
    """Try to extract keyword from JSON-LD or meta description in the TSX."""
    # Try JSON-LD description field
    m = re.search(r'"description"\s*:\s*"([^"]+)"', tsx_text)
    if m:
        desc = m.group(1)
        # Use first few meaningful words as keyword approximation
        words = [w for w in re.findall(r"[a-zA-Z]+", desc.lower()) if len(w) > 3]
        if len(words) >= 2:
            return " ".join(words[:3])
    return ""


def run_qc(article: str, keyword: str, h2_count: int) -> dict:
    """Run quality checks, matching content_factory.py stage4_qc logic exactly."""
    word_count = len(article.split())

    ai_found = [p for p in AI_PHRASES if p.lower() in article.lower()]
    human_found = [m for m in HUMAN_MARKERS if m.lower() in article.lower()]
    internal_links = re.findall(
        r"tempmails\.top|href=['\"]/", article, re.IGNORECASE
    )
    kw_count = article.lower().count(keyword.lower()) if keyword else 0

    checks = {
        "word_count": {"value": word_count, "pass": 1200 <= word_count <= 3500},
        "ai_phrases": {"value": len(ai_found), "found": ai_found, "pass": len(ai_found) == 0},
        "human_markers": {"value": len(human_found), "found": human_found, "pass": len(human_found) >= 2},
        "h2_count": {"value": h2_count, "pass": h2_count >= 3},
        "internal_links": {"value": len(internal_links), "pass": len(internal_links) >= 1},
        "keyword_occurrences": {"value": kw_count, "pass": kw_count >= 2},
    }

    fail_count = sum(1 for c in checks.values() if not c["pass"])
    all_pass = fail_count <= 2

    return {
        "keyword": keyword,
        "timestamp": datetime.now().isoformat(),
        "overall": "PASS" if all_pass else "FAIL",
        "fail_count": fail_count,
        "checks": checks,
    }


def main():
    DOCS_DIR.mkdir(exist_ok=True)

    tsx_files = sorted(BLOG_DIR.glob("blog.*.tsx"))
    if not tsx_files:
        print("No blog TSX files found.")
        return

    pass_count = 0
    fail_count = 0
    skip_count = 0

    for tsx_path in tsx_files:
        slug = tsx_path.stem.replace("blog.", "")  # e.g. "best-temporary-email-services-2026"
        qc_path = DOCS_DIR / f"qc-{slug}.json"

        if qc_path.exists():
            print(f"  SKIP  {slug} (QC report already exists)")
            skip_count += 1
            continue

        tsx_text = tsx_path.read_text(encoding="utf-8")
        article, h2_count = extract_content(tsx_text)

        if not article:
            print(f"  WARN  {slug} (could not extract prose content)")
            continue

        keyword = extract_keyword(tsx_text)
        report = run_qc(article, keyword, h2_count)

        qc_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        status = report["overall"]
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1

        fails = report["fail_count"]
        print(f"  {status:4s}  {slug} ({fails} check(s) failed)")

    print(f"\nSummary: {pass_count} PASS, {fail_count} FAIL, {skip_count} SKIPPED")


if __name__ == "__main__":
    main()
