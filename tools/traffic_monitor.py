#!/usr/bin/env python3
"""
Traffic Monitor — GSC data analysis for CrazyMail sites.

Usage:
    python tools/traffic_monitor.py                    # API mode, last 28 days
    python tools/traffic_monitor.py --csv data.csv     # CSV import mode
    python tools/traffic_monitor.py --days 7           # Last 7 days
    python tools/traffic_monitor.py --opportunities    # Only show opportunities
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CREDENTIALS_PATH = ROOT / "tools" / "gsc_credentials.json"
SITE_PROPERTY = "https://tempmails.top/"

# ── Setup Instructions ─────────────────────────────────────────────────────
SETUP_INSTRUCTIONS = """\
══════════════════════════════════════════════════════════════
  GSC Credentials Not Found
══════════════════════════════════════════════════════════════

To use API mode, you need Google Search Console OAuth2 credentials.

Steps:

1. Go to Google Cloud Console:
   https://console.cloud.google.com/apis/credentials

2. Create or select a project

3. Enable the Search Console API:
   https://console.cloud.google.com/apis/library/searchconsole.googleapis.com

4. Create OAuth 2.0 Client ID:
   - Application type: Desktop app
   - Download the JSON file

5. Save the downloaded file as:
   {credentials_path}

6. Run this script again. It will print an authorization URL.
   Visit the URL, grant access, and paste the code back.

Alternatively, use CSV mode:
  python tools/traffic_monitor.py --csv path/to/gsc_export.csv

══════════════════════════════════════════════════════════════
""".format(credentials_path=CREDENTIALS_PATH)


# ── GSC API Mode ───────────────────────────────────────────────────────────
def get_gsc_service():
    """Build GSC API service from OAuth2 credentials."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: google-api-python-client or google-auth-oauthlib not installed.")
        print("Run: pip install google-api-python-client google-auth-oauthlib")
        sys.exit(1)

    SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
    creds = None

    token_path = ROOT / "tools" / "gsc_token.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                print(SETUP_INSTRUCTIONS)
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

        token_path.write_text(creds.to_json(), encoding="utf-8")
        print(f"Credentials saved to {token_path}")

    return build("searchconsole", "v1", credentials=creds)


def fetch_gsc_data(service, site: str, days: int) -> list[dict]:
    """Fetch search analytics data from GSC API."""
    end_date = datetime.now() - timedelta(days=3)
    start_date = end_date - timedelta(days=days)

    print(f"Fetching GSC data: {start_date.date()} to {end_date.date()} ...")

    all_rows = []
    start_row = 0
    row_limit = 5000

    while True:
        request_body = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["query", "page"],
            "rowLimit": row_limit,
            "startRow": start_row,
        }

        response = (
            service.searchanalytics()
            .query(siteUrl=site, body=request_body)
            .execute()
        )

        rows = response.get("rows", [])
        if not rows:
            break

        for row in rows:
            keys = row.get("keys", [])
            all_rows.append({
                "query": keys[0] if len(keys) > 0 else "",
                "page": keys[1] if len(keys) > 1 else "",
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0),
            })

        if len(rows) < row_limit:
            break
        start_row += row_limit

    print(f"  Fetched {len(all_rows)} rows")
    return all_rows


def fetch_gsc_daily(service, site: str, days: int) -> list[dict]:
    """Fetch daily aggregated data for trend analysis."""
    end_date = datetime.now() - timedelta(days=3)
    start_date = end_date - timedelta(days=days)

    request_body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "dimensions": ["date"],
        "rowLimit": 1000,
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site, body=request_body)
        .execute()
    )

    daily = []
    for row in response.get("rows", []):
        daily.append({
            "date": row["keys"][0],
            "clicks": row.get("clicks", 0),
            "impressions": row.get("impressions", 0),
            "ctr": row.get("ctr", 0),
            "position": row.get("position", 0),
        })

    return daily


# ── CSV Import Mode ────────────────────────────────────────────────────────
def load_csv_data(csv_path: str) -> list[dict]:
    """Load GSC exported CSV data."""
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # GSC CSV export uses these column names (may vary by locale)
            # Try common column name variations
            query = (
                row.get("Query")
                or row.get("query")
                or row.get("Top queries")
                or row.get("查询")
                or ""
            )
            page = (
                row.get("Page")
                or row.get("page")
                or row.get("Top pages")
                or row.get("页面")
                or ""
            )
            clicks = _parse_int(
                row.get("Clicks")
                or row.get("clicks")
                or row.get("点击次数")
                or "0"
            )
            impressions = _parse_int(
                row.get("Impressions")
                or row.get("impressions")
                or row.get("展示次数")
                or "0"
            )
            ctr = _parse_float(
                row.get("CTR")
                or row.get("ctr")
                or row.get("点击率")
                or "0"
            )
            position = _parse_float(
                row.get("Position")
                or row.get("position")
                or row.get("排名")
                or "0"
            )

            # CTR in GSC CSV is percentage (e.g., 5.2%), convert to decimal
            if ctr > 1:
                ctr = ctr / 100.0

            rows.append({
                "query": query,
                "page": page,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "position": position,
            })

    print(f"Loaded {len(rows)} rows from CSV")
    return rows


def _parse_int(val: str) -> int:
    try:
        return int(val.replace(",", "").replace(" ", ""))
    except (ValueError, AttributeError):
        return 0


def _parse_float(val: str) -> float:
    try:
        return float(val.replace(",", "").replace("%", "").replace(" ", ""))
    except (ValueError, AttributeError):
        return 0.0


# ── Analysis ───────────────────────────────────────────────────────────────
def compute_summary(rows: list[dict]) -> dict:
    """Compute overall summary metrics."""
    total_clicks = sum(r["clicks"] for r in rows)
    total_impressions = sum(r["impressions"] for r in rows)
    avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    avg_position = (
        sum(r["position"] * r["impressions"] for r in rows) / total_impressions
        if total_impressions > 0
        else 0
    )

    return {
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "avg_ctr": round(avg_ctr, 4),
        "avg_position": round(avg_position, 1),
    }


def get_top_queries(rows: list[dict], limit: int = 10) -> list[dict]:
    """Get top queries by clicks."""
    query_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "positions": []})

    for r in rows:
        if not r["query"]:
            continue
        q = query_stats[r["query"]]
        q["clicks"] += r["clicks"]
        q["impressions"] += r["impressions"]
        q["positions"].append(r["position"])

    result = []
    for query, stats in query_stats.items():
        avg_pos = sum(stats["positions"]) / len(stats["positions"]) if stats["positions"] else 0
        avg_ctr = stats["clicks"] / stats["impressions"] if stats["impressions"] > 0 else 0
        result.append({
            "query": query,
            "clicks": stats["clicks"],
            "impressions": stats["impressions"],
            "ctr": round(avg_ctr, 4),
            "position": round(avg_pos, 1),
        })

    result.sort(key=lambda x: x["clicks"], reverse=True)
    return result[:limit]


def get_top_pages(rows: list[dict], limit: int = 10) -> list[dict]:
    """Get top pages by clicks."""
    page_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "positions": []})

    for r in rows:
        if not r["page"]:
            continue
        p = page_stats[r["page"]]
        p["clicks"] += r["clicks"]
        p["impressions"] += r["impressions"]
        p["positions"].append(r["position"])

    result = []
    for page, stats in page_stats.items():
        avg_pos = sum(stats["positions"]) / len(stats["positions"]) if stats["positions"] else 0
        avg_ctr = stats["clicks"] / stats["impressions"] if stats["impressions"] > 0 else 0
        result.append({
            "page": page,
            "clicks": stats["clicks"],
            "impressions": stats["impressions"],
            "ctr": round(avg_ctr, 4),
            "position": round(avg_pos, 1),
        })

    result.sort(key=lambda x: x["clicks"], reverse=True)
    return result[:limit]


def find_low_ctr_opportunities(rows: list[dict], limit: int = 10) -> list[dict]:
    """Find queries with high impressions but low CTR (optimization opportunities)."""
    query_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "positions": []})

    for r in rows:
        if not r["query"]:
            continue
        q = query_stats[r["query"]]
        q["clicks"] += r["clicks"]
        q["impressions"] += r["impressions"]
        q["positions"].append(r["position"])

    overall_ctr = sum(r["clicks"] for r in rows) / sum(r["impressions"] for r in rows) if sum(r["impressions"] for r in rows) > 0 else 0

    opportunities = []
    for query, stats in query_stats.items():
        if stats["impressions"] < 10:
            continue
        avg_pos = sum(stats["positions"]) / len(stats["positions"])
        query_ctr = stats["clicks"] / stats["impressions"] if stats["impressions"] > 0 else 0

        # High impressions + CTR below average = opportunity
        if query_ctr < overall_ctr and stats["impressions"] >= 20:
            opportunities.append({
                "query": query,
                "clicks": stats["clicks"],
                "impressions": stats["impressions"],
                "ctr": round(query_ctr, 4),
                "position": round(avg_pos, 1),
                "ctr_gap": round(overall_ctr - query_ctr, 4),
            })

    opportunities.sort(key=lambda x: x["impressions"], reverse=True)
    return opportunities[:limit]


def find_ranking_5_20(rows: list[dict], limit: int = 20) -> list[dict]:
    """Find keywords ranking positions 5-20 (room for improvement)."""
    query_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "positions": []})

    for r in rows:
        if not r["query"]:
            continue
        q = query_stats[r["query"]]
        q["clicks"] += r["clicks"]
        q["impressions"] += r["impressions"]
        q["positions"].append(r["position"])

    result = []
    for query, stats in query_stats.items():
        avg_pos = sum(stats["positions"]) / len(stats["positions"])
        if 5 <= avg_pos <= 20:
            avg_ctr = stats["clicks"] / stats["impressions"] if stats["impressions"] > 0 else 0
            result.append({
                "query": query,
                "clicks": stats["clicks"],
                "impressions": stats["impressions"],
                "ctr": round(avg_ctr, 4),
                "position": round(avg_pos, 1),
            })

    result.sort(key=lambda x: x["impressions"], reverse=True)
    return result[:limit]


def find_new_queries(rows: list[dict], recent_days: int = 7) -> list[dict]:
    """Find queries that appear to be new (low total clicks, may be emerging)."""
    query_stats = defaultdict(lambda: {"clicks": 0, "impressions": 0, "positions": []})

    for r in rows:
        if not r["query"]:
            continue
        q = query_stats[r["query"]]
        q["clicks"] += r["clicks"]
        q["impressions"] += r["impressions"]
        q["positions"].append(r["position"])

    # New queries = low clicks but getting impressions (emerging)
    new_queries = []
    for query, stats in query_stats.items():
        if stats["clicks"] <= 3 and stats["impressions"] >= 5:
            avg_pos = sum(stats["positions"]) / len(stats["positions"])
            new_queries.append({
                "query": query,
                "clicks": stats["clicks"],
                "impressions": stats["impressions"],
                "ctr": round(stats["clicks"] / stats["impressions"], 4) if stats["impressions"] > 0 else 0,
                "position": round(avg_pos, 1),
            })

    new_queries.sort(key=lambda x: x["impressions"], reverse=True)
    return new_queries[:15]


def analyze(rows: list[dict], opportunities_only: bool = False) -> dict:
    """Run full analysis on the data."""
    summary = compute_summary(rows)

    result = {
        "summary": summary,
    }

    if not opportunities_only:
        result["top_queries"] = get_top_queries(rows)
        result["top_pages"] = get_top_pages(rows)

    result["opportunities"] = {
        "low_ctr_high_impressions": find_low_ctr_opportunities(rows),
        "ranking_5_to_20": find_ranking_5_20(rows),
        "new_queries": find_new_queries(rows),
    }

    return result


# ── Report Output ──────────────────────────────────────────────────────────
def write_json_report(report: dict, date_str: str) -> Path:
    """Write JSON report to docs/."""
    DOCS.mkdir(exist_ok=True)
    path = DOCS / f"traffic-report-{date_str}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_markdown_report(report: dict, date_str: str) -> Path:
    """Write Markdown summary to docs/."""
    DOCS.mkdir(exist_ok=True)
    path = DOCS / f"traffic-report-{date_str}.md"

    summary = report["summary"]
    lines = [
        f"# Traffic Monitor Report - {date_str}",
        "",
        f"**Site:** {report['site']}",
        f"**Period:** {report['period']}",
        f"**Generated:** {report['generated_at']}",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Clicks | {summary['total_clicks']:,} |",
        f"| Total Impressions | {summary['total_impressions']:,} |",
        f"| Average CTR | {summary['avg_ctr']:.2%} |",
        f"| Average Position | {summary['avg_position']:.1f} |",
        "",
    ]

    # Top Queries
    top_queries = report.get("top_queries", [])
    if top_queries:
        lines.extend([
            "## Top Queries",
            "",
            "| Query | Clicks | Impressions | CTR | Position |",
            "|-------|--------|-------------|-----|----------|",
        ])
        for q in top_queries:
            lines.append(
                f"| {q['query']} | {q['clicks']:,} | {q['impressions']:,} | {q['ctr']:.2%} | {q['position']:.1f} |"
            )
        lines.append("")

    # Top Pages
    top_pages = report.get("top_pages", [])
    if top_pages:
        lines.extend([
            "## Top Pages",
            "",
            "| Page | Clicks | Impressions | CTR | Position |",
            "|------|--------|-------------|-----|----------|",
        ])
        for p in top_pages:
            page_short = p["page"].replace("https://tempmails.top", "")
            lines.append(
                f"| {page_short} | {p['clicks']:,} | {p['impressions']:,} | {p['ctr']:.2%} | {p['position']:.1f} |"
            )
        lines.append("")

    # Opportunities
    opps = report.get("opportunities", {})

    low_ctr = opps.get("low_ctr_high_impressions", [])
    if low_ctr:
        lines.extend([
            "## Optimization Opportunities",
            "",
            "### High Impressions, Low CTR (optimize title/description)",
            "",
            "| Query | Impressions | CTR | Position | CTR Gap |",
            "|-------|-------------|-----|----------|---------|",
        ])
        for q in low_ctr:
            lines.append(
                f"| {q['query']} | {q['impressions']:,} | {q['ctr']:.2%} | {q['position']:.1f} | {q['ctr_gap']:.2%} |"
            )
        lines.append("")

    ranking_5_20 = opps.get("ranking_5_to_20", [])
    if ranking_5_20:
        lines.extend([
            "### Ranking Positions 5-20 (room to improve)",
            "",
            "| Query | Clicks | Impressions | CTR | Position |",
            "|-------|--------|-------------|-----|----------|",
        ])
        for q in ranking_5_20:
            lines.append(
                f"| {q['query']} | {q['clicks']:,} | {q['impressions']:,} | {q['ctr']:.2%} | {q['position']:.1f} |"
            )
        lines.append("")

    new_queries = opps.get("new_queries", [])
    if new_queries:
        lines.extend([
            "### New / Emerging Queries",
            "",
            "| Query | Clicks | Impressions | CTR | Position |",
            "|-------|--------|-------------|-----|----------|",
        ])
        for q in new_queries:
            lines.append(
                f"| {q['query']} | {q['clicks']:,} | {q['impressions']:,} | {q['ctr']:.2%} | {q['position']:.1f} |"
            )
        lines.append("")

    # Action items
    lines.extend([
        "## Recommended Actions",
        "",
    ])

    if low_ctr:
        lines.append(f"1. **Optimize title/description** for {len(low_ctr)} high-impression, low-CTR queries")
    if ranking_5_20:
        lines.append(f"2. **Improve content** for {len(ranking_5_20)} keywords ranking 5-20")
    if new_queries:
        lines.append(f"3. **Create content** for {len(new_queries)} new/emerging queries")

    if not low_ctr and not ranking_5_20 and not new_queries:
        lines.append("No immediate opportunities found. Keep monitoring.")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by CrazyMail Traffic Monitor*")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def print_console_summary(report: dict, opportunities_only: bool = False):
    """Print a summary to console."""
    summary = report["summary"]

    print()
    print("=" * 60)
    print("  Traffic Monitor Report")
    print("=" * 60)
    print(f"  Site:     {report['site']}")
    print(f"  Period:   {report['period']}")
    print()
    print(f"  Clicks:      {summary['total_clicks']:,}")
    print(f"  Impressions: {summary['total_impressions']:,}")
    print(f"  Avg CTR:     {summary['avg_ctr']:.2%}")
    print(f"  Avg Position:{summary['avg_position']:.1f}")
    print()

    if not opportunities_only:
        top_queries = report.get("top_queries", [])
        if top_queries:
            print("Top Queries:")
            print("-" * 60)
            for i, q in enumerate(top_queries[:5], 1):
                print(f"  {i}. {q['query'][:40]:40s}  clicks={q['clicks']:>5}  pos={q['position']:.1f}")
            print()

        top_pages = report.get("top_pages", [])
        if top_pages:
            print("Top Pages:")
            print("-" * 60)
            for i, p in enumerate(top_pages[:5], 1):
                page_short = p["page"].replace("https://tempmails.top", "") or "/"
                print(f"  {i}. {page_short[:40]:40s}  clicks={p['clicks']:>5}  pos={p['position']:.1f}")
            print()

    opps = report.get("opportunities", {})

    low_ctr = opps.get("low_ctr_high_impressions", [])
    if low_ctr:
        print(f"Opportunities: {len(low_ctr)} high-impression, low-CTR queries")
        for q in low_ctr[:3]:
            print(f"  - {q['query'][:40]}  imp={q['impressions']}  ctr={q['ctr']:.2%}")
        print()

    ranking_5_20 = opps.get("ranking_5_to_20", [])
    if ranking_5_20:
        print(f"Keywords ranking 5-20: {len(ranking_5_20)}")
        for q in ranking_5_20[:3]:
            print(f"  - {q['query'][:40]}  pos={q['position']:.1f}  imp={q['impressions']}")
        print()

    new_queries = opps.get("new_queries", [])
    if new_queries:
        print(f"New/emerging queries: {len(new_queries)}")
        for q in new_queries[:3]:
            print(f"  - {q['query'][:40]}  imp={q['impressions']}")
        print()


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Traffic Monitor — GSC data analysis for CrazyMail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python tools/traffic_monitor.py
  python tools/traffic_monitor.py --csv data.csv
  python tools/traffic_monitor.py --days 7
  python tools/traffic_monitor.py --opportunities
        """,
    )
    parser.add_argument(
        "--csv",
        help="Path to GSC exported CSV file (enables CSV import mode)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=28,
        help="Number of days to analyze (default: 28)",
    )
    parser.add_argument(
        "--opportunities",
        action="store_true",
        help="Only show optimization opportunities",
    )

    args = parser.parse_args()

    # Load data based on mode
    if args.csv:
        print(f"CSV Import Mode: {args.csv}")
        rows = load_csv_data(args.csv)
        period_label = f"CSV import ({Path(args.csv).name})"
    else:
        if not CREDENTIALS_PATH.exists():
            print(SETUP_INSTRUCTIONS)
            sys.exit(1)

        print("API Mode: Connecting to Google Search Console ...")
        service = get_gsc_service()
        rows = fetch_gsc_data(service, SITE_PROPERTY, args.days)
        period_end = datetime.now() - timedelta(days=3)
        period_start = period_end - timedelta(days=args.days)
        period_label = f"{period_start.date()} to {period_end.date()}"

    if not rows:
        print("No data found. Check your CSV file or GSC property settings.")
        sys.exit(1)

    # Analyze
    report_data = analyze(rows, opportunities_only=args.opportunities)

    date_str = datetime.now().strftime("%Y-%m-%d")
    report = {
        "generated_at": datetime.now().isoformat(),
        "site": SITE_PROPERTY,
        "period": period_label,
        "mode": "csv" if args.csv else "api",
        **report_data,
    }

    # Output
    json_path = write_json_report(report, date_str)
    md_path = write_markdown_report(report, date_str)

    print_console_summary(report, opportunities_only=args.opportunities)

    print(f"Reports saved:")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")
    print()


if __name__ == "__main__":
    main()
