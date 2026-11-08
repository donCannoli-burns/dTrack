#!/usr/bin/env python3
"""Read-only, optional NumPy analysis of KoLmafia dTrack checkpoint history.

This is an offline helper, not an ASH/KoLmafia dependency. It never changes a
checkpoint or queries prices; asset figures are the historical saved values.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("NumPy is required for this optional helper: python3 -m pip install numpy") from exc

DATE_RE = re.compile(r"^\d{8}$")
EVENT_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def rows(path: Path, min_columns: int):
    """Return well-formed TSV rows; ignore absent files and incomplete lines."""
    if not path.is_file():
        return []
    result = []
    with path.open("r", encoding="utf-8-sig") as source:
        for line in source:
            if not line.strip():
                continue
            parts = line.rstrip("\r\n").split("\t")
            if len(parts) >= min_columns:
                result.append(parts)
    return result


def history(data_dir: Path):
    """Load checkpoint meat and historical net worth; no fresh price lookups."""
    meat = {}
    for parts in rows(data_dir / "meat.txt", 4):
        date, event = parts[:2]
        if not DATE_RE.fullmatch(date) or not EVENT_RE.fullmatch(event):
            continue
        try:
            adventures = int(parts[2])
            liquid = int(parts[3])
            timestamp = int(parts[5]) if len(parts) > 5 and parts[5] else 0
        except ValueError:
            continue
        meat[(date, event)] = (adventures, liquid, timestamp)

    networth = {}
    for parts in rows(data_dir / "networth_checkpoints.txt", 4):
        key = tuple(parts[:2])
        if not DATE_RE.fullmatch(key[0]) or not EVENT_RE.fullmatch(key[1]):
            continue
        try:
            networth[key] = int(parts[3])
        except ValueError:
            continue

    ordered = sorted(meat, key=lambda key: (
        key[0], meat[key][2] if meat[key][2] else 0, meat[key][0], key[1]
    ))
    return ordered, meat, networth


def analyze(data_dir: Path):
    """Vectorize differences across all saved checkpoints, preserving gaps."""
    ordered, meat, networth = history(data_dir)
    if not ordered:
        return {"checkpoints": [], "intervals": [], "count": 0, "valued_count": 0}

    adventures = np.asarray([meat[k][0] for k in ordered], dtype=np.int64)
    liquid = np.asarray([meat[k][1] for k in ordered], dtype=np.int64)
    asset = np.asarray([networth.get(k, 0) for k in ordered], dtype=np.int64)
    has_asset = np.asarray([k in networth for k in ordered], dtype=np.bool_)
    # The numerical work is performed on aligned NumPy arrays. For missing
    # snapshots, historical item deltas stay unknown (not manufactured zeros).
    adv_deltas = np.diff(adventures)
    meat_deltas = np.diff(liquid)
    item_deltas = np.diff(asset)
    complete_pairs = has_asset[1:] & has_asset[:-1]
    total_deltas = meat_deltas + item_deltas

    checkpoints = []
    for i, (date, event) in enumerate(ordered):
        checkpoints.append({
            "date": date,
            "event": event,
            "adventures": int(adventures[i]),
            "liquid_meat": int(liquid[i]),
            "historical_item_value": int(asset[i]) if has_asset[i] else None,
            "historical_total": int(liquid[i] + asset[i]) if has_asset[i] else None,
        })

    intervals = []
    for i in range(len(adv_deltas)):
        valued = bool(complete_pairs[i])
        turns = int(adv_deltas[i])
        meat_change = int(meat_deltas[i])
        total_change = int(total_deltas[i]) if valued else None
        intervals.append({
            "from": f"{ordered[i][0]} {ordered[i][1]}",
            "to": f"{ordered[i+1][0]} {ordered[i+1][1]}",
            "adventure_delta": turns,
            "meat_delta": meat_change,
            "item_delta": int(item_deltas[i]) if valued else None,
            "total_delta": total_change,
            "meat_per_adventure": meat_change / turns if turns > 0 else None,
            "total_per_adventure": total_change / turns if turns > 0 and valued else None,
        })

    return {
        "count": len(checkpoints),
        "valued_count": int(np.count_nonzero(has_asset)),
        "checkpoints": checkpoints,
        "intervals": intervals,
        "note": "Historical checkpoint prices; not a fresh mall valuation. "
                "Intervals crossing ascensions or resets may not be economically comparable.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path,
                        help="KoLmafia data/Profit Tracking/<character> directory")
    parser.add_argument("--indent", type=int, default=2, choices=(0, 2, 4))
    args = parser.parse_args(argv)
    print(json.dumps(analyze(args.data_dir), indent=args.indent, allow_nan=False))


if __name__ == "__main__":
    main()
