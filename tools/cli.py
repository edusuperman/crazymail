#!/usr/bin/env python3
"""
CrazyMail CLI — Unified entry point for all content pipeline tools.

Usage:
    python tools/cli.py discover "temporary email" "disposable email"
    python tools/cli.py produce "temporary email for verification"
    python tools/cli.py batch -n 5
    python tools/cli.py deploy
    python tools/cli.py status
    python tools/cli.py audit
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
DOCS = ROOT / "docs"
SITE_FRONTEND = ROOT / "sites" / "site-01" / "frontend"


def run_subprocess(cmd: list[str], cwd: Path = ROOT) -> int:
    """Run a subprocess, streaming output in real-time. Returns exit code."""
    print(f"\n{'─'*60}")
    print(f"$ {' '.join(str(c) for c in cmd)}")
    print(f"{'─'*60}")
    result = subprocess.run(
        [str(c) for c in cmd],
        cwd=str(cwd),
        shell=True,
    )
    return result.returncode


def capture_subprocess(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    """Run a subprocess and capture output. Returns (exit_code, stdout)."""
    result = subprocess.run(
        [str(c) for c in cmd],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=True,
    )
    output = result.stdout + result.stderr
    return result.returncode, output


# ── Subcommands ────────────────────────────────────────────────────────────

def cmd_discover(args):
    """Run keyword discovery with given seed keywords."""
    seeds = args.seeds
    print(f"Discovering keywords from seeds: {', '.join(seeds)}")
    cmd = [sys.executable, str(TOOLS / "keyword_discovery.py")] + seeds
    return run_subprocess(cmd)


def cmd_produce(args):
    """Run content factory for one keyword."""
    keyword = args.keyword
    print(f"Producing content for: {keyword}")
    cmd = [sys.executable, str(TOOLS / "content_factory.py"), keyword]
    return run_subprocess(cmd)


def cmd_batch(args):
    """Run content factory for N keywords from latest discovery."""
    count = args.n

    # Find latest keyword-discovery-*.json
    discovery_files = sorted(DOCS.glob("keyword-discovery-*.json"), reverse=True)
    if not discovery_files:
        print("Error: No keyword-discovery-*.json found in docs/")
        return 1

    latest = discovery_files[0]
    print(f"Reading keywords from: {latest.name}")

    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {latest.name}: {e}")
        return 1

    # Filter uncovered keywords
    uncovered = [
        kw for kw in data.get("keywords", [])
        if not kw.get("already_covered", True)
    ]

    if not uncovered:
        print("No uncovered keywords found. Run discover first.")
        return 0

    # Take top N
    batch = uncovered[:count]
    print(f"\nBatch: {len(batch)} keywords to process (requested {count})")

    results = {"attempted": 0, "qc_pass": 0, "qc_fail": 0}

    for i, kw_data in enumerate(batch, 1):
        keyword = kw_data["keyword"]
        print(f"\n{'='*60}")
        print(f"[{i}/{len(batch)}] {keyword}")
        print(f"{'='*60}")

        cmd = [sys.executable, str(TOOLS / "content_factory.py"), keyword]
        exit_code = run_subprocess(cmd)
        results["attempted"] += 1

        # Check QC result from content_factory output
        # The content_factory prints QC status at the end
        if exit_code == 0:
            results["qc_pass"] += 1
        else:
            results["qc_fail"] += 1

    # Run deploy check to show results
    print(f"\n{'='*60}")
    print("Running deployment gate check...")
    print(f"{'='*60}")
    run_subprocess([sys.executable, str(TOOLS / "deploy.py"), "--check-only"])

    # Print summary
    print(f"\n{'='*60}")
    print("Batch Summary")
    print(f"{'='*60}")
    print(f"  Attempted: {results['attempted']}")
    print(f"  QC PASS:   {results['qc_pass']}")
    print(f"  QC FAIL:   {results['qc_fail']}")
    print(f"{'='*60}\n")

    return 0


def cmd_deploy(args):
    """Run deploy gate check, then build and deploy if checks pass."""
    # Step 1: Run check
    print("Running deployment gate check...")
    exit_code, output = capture_subprocess(
        [sys.executable, str(TOOLS / "deploy.py"), "--check-only"]
    )
    print(output)

    # Parse check output for QC FAIL
    if "QC FAIL" in output and "should remove" in output:
        print("\n✖ DEPLOYMENT BLOCKED: QC FAIL articles found!")
        print("Fix or remove the failing articles before deploying.")
        return 1

    if exit_code != 0:
        print("\n✖ Deployment check failed!")
        return exit_code

    # Step 2: Build
    print("\nBuilding frontend...")
    exit_code = run_subprocess(
        ["npm", "run", "build"],
        cwd=SITE_FRONTEND,
    )
    if exit_code != 0:
        print("\n✖ Build failed!")
        return exit_code

    # Step 3: Deploy
    print("\nDeploying to Vercel...")
    exit_code = run_subprocess(
        ["vercel", "--prod", "--yes", "--name", "crazymail"],
        cwd=ROOT,
    )
    if exit_code != 0:
        print("\n✖ Deploy failed!")
        return exit_code

    print("\n✔ Deployment complete!")
    return 0


def cmd_status(args):
    """Show current project status."""
    print(f"\n{'='*60}")
    print("CrazyMail Project Status")
    print(f"{'='*60}")

    # Article count
    routes_dir = ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"
    tsx_files = list(routes_dir.glob("blog.*.tsx")) if routes_dir.exists() else []
    print(f"\n  Blog articles (TSX): {len(tsx_files)}")

    # QC stats
    qc_files = sorted(DOCS.glob("qc-*.json"))
    qc_pass = 0
    qc_fail = 0
    for qc_file in qc_files:
        try:
            data = json.loads(qc_file.read_text(encoding="utf-8"))
            if data.get("overall") == "PASS":
                qc_pass += 1
            else:
                qc_fail += 1
        except (json.JSONDecodeError, OSError):
            pass
    print(f"  QC reports: {len(qc_files)} (PASS: {qc_pass}, FAIL: {qc_fail})")

    # Latest keyword discovery
    discovery_files = sorted(DOCS.glob("keyword-discovery-*.json"), reverse=True)
    if discovery_files:
        latest = discovery_files[0]
        print(f"\n  Latest discovery: {latest.name}")
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            total = data.get("total_discovered", "?")
            covered = data.get("already_covered_count", "?")
            new = data.get("new_keywords_count", "?")
            print(f"    Total keywords: {total}")
            print(f"    Already covered: {covered}")
            print(f"    New/uncovered: {new}")
        except (json.JSONDecodeError, OSError):
            print("    (Could not read discovery file)")
    else:
        print("\n  No keyword discovery files found.")

    # Latest content run
    content_files = sorted(DOCS.glob("content-factory-*.json"), reverse=True)
    if content_files:
        print(f"\n  Latest content run: {content_files[0].name}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_audit(args):
    """Run deploy gate check and display the report."""
    print("Running deployment audit...")
    exit_code, output = capture_subprocess(
        [sys.executable, str(TOOLS / "deploy.py"), "--check-only"]
    )
    print(output)
    return exit_code


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="crazymail",
        description="CrazyMail CLI — Content pipeline management tool",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # discover
    p_discover = subparsers.add_parser(
        "discover",
        help="Run keyword discovery from seed keywords",
    )
    p_discover.add_argument(
        "seeds",
        nargs="+",
        help="Seed keywords for discovery",
    )

    # produce
    p_produce = subparsers.add_parser(
        "produce",
        help="Run content factory for one keyword",
    )
    p_produce.add_argument(
        "keyword",
        help="Keyword to produce content for",
    )

    # batch
    p_batch = subparsers.add_parser(
        "batch",
        help="Run content factory for N uncovered keywords",
    )
    p_batch.add_argument(
        "-n",
        type=int,
        default=3,
        help="Number of keywords to process (default: 3)",
    )

    # deploy
    subparsers.add_parser(
        "deploy",
        help="Run deploy gate check + build + deploy",
    )

    # status
    subparsers.add_parser(
        "status",
        help="Show current project status",
    )

    # audit
    subparsers.add_parser(
        "audit",
        help="Run deploy gate check and display report",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "discover": cmd_discover,
        "produce": cmd_produce,
        "batch": cmd_batch,
        "deploy": cmd_deploy,
        "status": cmd_status,
        "audit": cmd_audit,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
