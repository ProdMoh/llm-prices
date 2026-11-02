"""Check the data files against the schema and a few rules the schema cannot express.

Run: pip install jsonschema && python scripts/validate.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    prices = json.loads((ROOT / "data/prices.json").read_text())
    schema = json.loads((ROOT / "schema/prices.schema.json").read_text())
    errors += [f"prices.json {'/'.join(map(str, e.path))}: {e.message}" for e in Draft202012Validator(schema).iter_errors(prices)]

    seen: set[tuple[str, str]] = set()
    for m in prices["models"]:
        key = (m["provider"], m["model"])
        if key in seen:
            errors.append(f"{key}: listed twice")
        seen.add(key)
        p = m["price_per_million_tokens"]
        if p.get("cached_input") is not None and p["cached_input"] >= p["input"]:
            errors.append(f"{key}: cached input is not cheaper than input")
        dates = [c["effective"] for c in m.get("scheduled_changes", [])]
        if dates != sorted(dates) or any(d <= prices["generated"] for d in dates):
            errors.append(f"{key}: scheduled changes must be future dates in order")

    rows = list(csv.DictReader((ROOT / "data/prices.csv").open()))
    if len(rows) != len(prices["models"]):
        errors.append(f"prices.csv has {len(rows)} rows for {len(prices['models'])} models")

    split = sum(len(json.loads(f.read_text())["models"]) for f in (ROOT / "data/providers").glob("*.json"))
    if split != len(prices["models"]):
        errors.append(f"data/providers has {split} models for {len(prices['models'])} in prices.json")

    shutdowns = json.loads((ROOT / "data/shutdowns.json").read_text())["shutdowns"]
    if [s["shutdown_date"] for s in shutdowns] != sorted(s["shutdown_date"] for s in shutdowns):
        errors.append("shutdowns.json is not sorted by date")

    for error in errors:
        print(error, file=sys.stderr)
    print(f"{len(prices['models'])} models, {len(shutdowns)} shutdown groups, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
