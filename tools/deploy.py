#!/usr/bin/env python3
"""
Deployment Gate Script for CrazyMail blog articles.

Scans QC reports and TSX files to ensure only PASS articles are deployed.
Blocks deployment if any deployed article has QC=FAIL.

Usage:
    python tools/deploy.py              # check + build + deploy
    python tools/deploy.py --check-only # check only, no deploy
    python tools/deploy.py --force      # skip QC check, deploy anyway
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE_ROUTES = ROOT / "sites" / "site-01" / "frontend" / "src" / "routes"


def load_qc_reports() -> dict[str, dict]:
    """Load all qc-*.json files from docs/. Returns {slug: qc_data}."""
    reports = {}
    for p in sorted(DOCS.glob("qc-*.json")):
        slug = p.stem.removeprefix("qc-")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            reports[slug] = data
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Warning: Could not read {p.name}: {e}")
    return reports


def find_tsx_slugs() -> set[str]:
    """Find all blog.*.tsx slugs in routes directory."""
    slugs = set()
    for p in SITE_ROUTES.glob("blog.*.tsx"):
        slug = p.stem.removeprefix("blog.")
        slugs.add(slug)
    return slugs


def run_check() -> tuple[list[str], list[str], list[str]]:
    """
    Run deployment gate check.

    Returns:
        (ok_slugs, fail_slugs, no_qc_slugs)
        - ok_slugs: TSX exists + QC PASS
        - fail_slugs: TSX exists + QC FAIL (should be removed)
        - no_qc_slugs: TSX exists but no QC report
    """
    qc_reports = load_qc_reports()
    tsx_slugs = find_tsx_slugs()

    ok_slugs = []
    fail_slugs = []
    no_qc_slugs = []

    for slug in sorted(tsx_slugs):
        if slug not in qc_reports:
            no_qc_slugs.append(slug)
        elif qc_reports[slug].get("overall") == "PASS":
            ok_slugs.append(slug)
        else:
            fail_slugs.append(slug)

    return ok_slugs, fail_slugs, no_qc_slugs


def print_report(ok_slugs, fail_slugs, no_qc_slugs):
    """Print the deployment gate report."""
    print(f"\n{'='*60}")
    print("Deployment Gate Report")
    print(f"{'='*60}")

    print(f"\n  QC PASS (deployed):     {len(ok_slugs)}")
    for s in ok_slugs:
        print(f"    ✓ {s}")

    if fail_slugs:
        print(f"\n  QC FAIL (should remove): {len(fail_slugs)}")
        for s in fail_slugs:
            print(f"    ✖ {s}")

    if no_qc_slugs:
        print(f"\n  No QC report:            {len(no_qc_slugs)}")
        for s in no_qc_slugs:
            print(f"    ? {s}")

    total = len(ok_slugs) + len(fail_slugs) + len(no_qc_slugs)
    print(f"\n  Total TSX files: {total}")
    print(f"{'='*60}\n")


def build_and_deploy():
    """Run build and deploy commands."""
    print("Building frontend...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=ROOT / "sites" / "site-01" / "frontend",
        shell=True,
    )
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    print("\nDeploying to Vercel...")
    result = subprocess.run(
        ["vercel", "--prod", "--yes", "--name", "crazymail"],
        cwd=ROOT,
        shell=True,
    )
    if result.returncode != 0:
        print("Deploy failed!")
        sys.exit(1)

    print("\nDeploy complete!")


def main():
    parser = argparse.ArgumentParser(
        description="CrazyMail deployment gate — ensures only QC-PASS articles are deployed",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only run QC check, do not build or deploy",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip QC check and deploy anyway (dangerous)",
    )
    args = parser.parse_args()

    if args.force:
        print("WARNING: --force flag set, skipping QC check!")
        build_and_deploy()
        return

    ok_slugs, fail_slugs, no_qc_slugs = run_check()
    print_report(ok_slugs, fail_slugs, no_qc_slugs)

    if fail_slugs:
        print("DEPLOYMENT BLOCKED: The following articles have QC=FAIL:")
        for s in fail_slugs:
            print(f"  - {s}")
        print("\nRemove these TSX files or fix the articles before deploying.")
        print("To remove: del sites/site-01/frontend/src/routes/blog.<slug>.tsx")
        sys.exit(1)

    if no_qc_slugs:
        print("WARNING: The following TSX files have no QC report:")
        for s in no_qc_slugs:
            print(f"  - {s}")
        print("These may have been created before the QC gate was added.")
        print("Consider running content_factory.py to generate QC reports.\n")

    if args.check_only:
        print("Check-only mode. All checks passed.")
        sys.exit(0)

    print("All checks passed. Proceeding with build and deploy...\n")
    build_and_deploy()


if __name__ == "__main__":
    main()
