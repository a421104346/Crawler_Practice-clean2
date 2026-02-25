from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


API_URL = "https://remotive.com/api/remote-jobs"


def _normalize_city(location: str) -> str:
    loc = (location or "").strip()
    if not loc:
        return "Unknown"
    # Common formats: "City, Country" / "Country" / "Worldwide"
    if "," in loc:
        return loc.split(",", 1)[0].strip() or loc.strip()
    return loc


def fetch_jobs(category: str | None, search: str | None, timeout: int = 30) -> dict[str, Any]:
    params: dict[str, str] = {}
    if category:
        params["category"] = category
    if search:
        params["search"] = search
    resp = requests.get(API_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape public job data (Remotive API) and export to CSV.")
    parser.add_argument("--category", default=None, help="Job category, e.g.: software-dev / data / devops (optional)")
    parser.add_argument("--search", default=None, help="Keyword search, e.g.: python / data analyst (optional)")
    parser.add_argument("--out", default=None, help="Output directory (default: recruit_analysis/output)")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    out_dir = Path(args.out).expanduser().resolve() if args.out else (base_dir / "output")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = fetch_jobs(args.category, args.search)
    jobs = data.get("jobs", [])

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw_path = out_dir / f"remotive_raw_{ts}.json"
    csv_path = out_dir / f"jobs_{ts}.csv"

    raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Flatten to CSV (fields: title, city, salary, publication date, skill tags...)
    rows: list[dict[str, Any]] = []
    for j in jobs:
        tags = j.get("tags") or []
        rows.append(
            {
                "id": j.get("id"),
                "title": j.get("title"),
                "company": j.get("company_name"),
                "city": _normalize_city(j.get("candidate_required_location") or ""),
                "location_raw": j.get("candidate_required_location"),
                "salary": j.get("salary"),
                "publication_date": j.get("publication_date"),
                "tags": "|".join([str(t).strip() for t in tags if str(t).strip()]),
                "category": j.get("category"),
                "job_type": j.get("job_type"),
                "url": j.get("url"),
            }
        )

    # Can write CSV without pandas (but later analysis will use pandas)
    import csv

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Scraping complete: {len(rows)} records")
    print(f"RAW: {raw_path}")
    print(f"CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


