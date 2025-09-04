#!/usr/bin/env python3
"""
make_metadata_from_filenames.py

Generate a metadata.csv from files named in the pattern:
    METHOD_LOCATION_SAMPLE_MODE_MAGNIFICATION.ext
Example:
    PCM_BIU_glassLube_NA_10x.jpg
"""
import argparse
import csv
import re
from pathlib import Path

DEFAULT_EXTS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".gif",
    ".webp",
    ".dcm",
]


def parse_filename(name: str):
    p = Path(name)
    ext = p.suffix
    stem = p.stem

    parts = stem.split("_")
    if len(parts) < 5:
        raise ValueError(
            (
                f"Expected at least 5 tokens separated by '_' but got {len(parts)}: "
                f"{stem}"
            )
        )

    method = parts[0]
    location = parts[1]
    if len(parts) == 5:
        sample = parts[2]
        mode = parts[3]
        magnification = parts[4]
    else:
        sample = "_".join(parts[2:-2])
        mode = parts[-2]
        magnification = parts[-1]

    mag_text = magnification
    tmp = mag_text.replace("_", ".")
    m = re.match(r"^\s*([0-9]+(\.[0-9]+)?)\s*[xX]?\s*$", tmp)
    mag_value = ""
    if m:
        try:
            mag_value = float(m.group(1))
        except Exception:
            mag_value = ""

    return {
        "method": method,
        "location": location,
        "sample": sample,
        "mode": mode,
        "magnification": mag_text,
        "magnification_value": mag_value,
        "ext": ext.lower(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=False, default="E:/OneDrive - University of Southampton/EDH BAM project - Shared Documents/General/Experiments/Vertical setup data/2025-09-03 new BS 8CB face up/unified data", help="Folder containing your images")
    ap.add_argument(
        "--ext", nargs="*", default=DEFAULT_EXTS, help="Extensions to include"
    )
    ap.add_argument("--csv-name", default="metadata.csv", help="Output CSV filename")
    args = ap.parse_args()

    root = Path(args.folder).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Folder not found or not a directory: {root}")

    exts = set([e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.ext])
    rows = []
    errors = []

    for p in sorted(root.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in exts:
            continue
        try:
            rec = parse_filename(p.name)
            rec_out = {
                "filename": p.name,
                "method": rec["method"],
                "location": rec["location"],
                "sample": rec["sample"],
                "mode": rec["mode"],
                "magnification": rec["magnification"],
                "magnification_value": rec["magnification_value"],
                "ext": rec["ext"],
                "rel_path": str(p.relative_to(root)),
            }
            rows.append(rec_out)
        except Exception as e:
            errors.append((p.name, str(e)))

    if not rows:
        print("No matching files found. Check your folder or --ext filters.")

    csv_path = root / args.csv_name
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename",
                "method",
                "location",
                "sample",
                "mode",
                "magnification",
                "magnification_value",
                "ext",
                "rel_path",   # was "abs_path"
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {csv_path}")
    if errors:
        print(f"Skipped {len(errors)} file(s):")
        for name, err in errors[:20]:
            print(f"  - {name}: {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more")


if __name__ == "__main__":
    main()
