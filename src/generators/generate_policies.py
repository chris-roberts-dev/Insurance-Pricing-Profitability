from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, fields
from datetime import date
from pathlib import Path

from .factories import PolicyRecord, PolicyRecordFactory


def serialize_value(value):
    if isinstance(value, date):
        return value.isoformat()

    if value is None:
        return ""

    return value


def serialize_record(record: PolicyRecord) -> dict:
    raw = asdict(record)
    return {key: serialize_value(value) for key, value in raw.items()}


def generate_policy_csv(rows: int, out_path: Path, chunk_size: int = 10_000) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    headers = [field.name for field in fields(PolicyRecord)]

    with out_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        rows_written = 0

        while rows_written < rows:
            current_chunk_size = min(chunk_size, rows - rows_written)

            batch = PolicyRecordFactory.build_batch(current_chunk_size)

            writer.writerows(serialize_record(record) for record in batch)

            rows_written += current_chunk_size

            print(f"Wrote {rows_written:,} / {rows:,} rows")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic auto insurance policy-term data."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=100_000,
        help="Number of policy-term rows to generate.",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/policy_terms.csv"),
        help="Output CSV path.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10_000,
        help="Number of rows to generate per chunk.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generate_policy_csv(
        rows=args.rows,
        out_path=args.out,
        chunk_size=args.chunk_size,
    )


if __name__ == "__main__":
    main()
