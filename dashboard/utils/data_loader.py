import json
from pathlib import Path
from typing import Any


DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"


def _read_json(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_outlines() -> list[dict]:
    results = []
    for p in sorted(DOCS_DIR.glob("outline-*.json")):
        data = _read_json(p)
        if data:
            data["_file"] = p.name
            results.append(data)
    return results


def load_qc_reports() -> list[dict]:
    results = []
    for p in sorted(DOCS_DIR.glob("qc-*.json")):
        data = _read_json(p)
        if data:
            data["_file"] = p.name
            results.append(data)
    return results


def load_keywords() -> list[dict]:
    results = []
    for p in sorted(DOCS_DIR.glob("keyword-discovery-*.json")):
        data = _read_json(p)
        if data:
            data["_file"] = p.name
            results.append(data)
    return results


def load_growth_content_dirs() -> list[dict]:
    results = []
    for d in sorted(DOCS_DIR.glob("growth-content-*")):
        if not d.is_dir():
            continue
        entry: dict[str, Any] = {
            "dir_name": d.name,
            "date": d.name.replace("growth-content-", ""),
            "files": [],
        }
        for f in sorted(d.iterdir()):
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                entry["files"].append(
                    {
                        "name": f.name,
                        "stem": f.stem,
                        "size_kb": round(f.stat().st_size / 1024, 1),
                        "content": content,
                    }
                )
        results.append(entry)
    return results


def get_simulation_traffic_data() -> dict:
    import random

    random.seed(42)
    days = []
    base_date = __import__("datetime").date(2026, 6, 1)
    for i in range(30):
        d = base_date + __import__("datetime").timedelta(days=i)
        clicks = random.randint(5, 80)
        impressions = clicks * random.randint(8, 25)
        ctr = round(clicks / impressions * 100, 2) if impressions else 0
        avg_position = round(random.uniform(8, 35), 1)
        days.append(
            {
                "date": d.isoformat(),
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "position": avg_position,
            }
        )
    return {
        "source": "simulation",
        "days": days,
        "total_clicks": sum(d["clicks"] for d in days),
        "total_impressions": sum(d["impressions"] for d in days),
        "avg_ctr": round(
            sum(d["clicks"] for d in days) / sum(d["impressions"] for d in days) * 100, 2
        )
        if sum(d["impressions"] for d in days)
        else 0,
        "avg_position": round(sum(d["position"] for d in days) / len(days), 1),
    }
