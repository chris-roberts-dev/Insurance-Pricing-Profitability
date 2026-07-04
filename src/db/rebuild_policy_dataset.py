from __future__ import annotations

import argparse

from src.db.bootstrap_postgres import (
    create_database_if_missing,
    create_policy_terms_table,
)

from src.generators.load_policies_to_postgres import load_policies_to_postgres


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild the synthetic policy table and load generated policy data."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=100_000,
        help="Number of synthetic policy records to generate and load.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10_000,
        help="Number of records to generate per batch.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    create_database_if_missing()
    create_policy_terms_table()

    load_policies_to_postgres(
        rows=args.rows,
        chunk_size=args.chunk_size,
        truncate=True,
    )


if __name__ == "__main__":
    main()
