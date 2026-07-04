from __future__ import annotations

import argparse
import os
from dataclasses import fields

import psycopg
from dotenv import load_dotenv

from .factories import PolicyRecord, PolicyRecordFactory

TABLE_NAME = "synthetic.policy_terms"


def get_connection_string() -> str:
    load_dotenv()

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "insurance_pricing")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise ValueError("POSTGRES_PASSWORD is missing. Add it to your .env file.")

    return (
        f"host={host} "
        f"port={port} "
        f"dbname={dbname} "
        f"user={user} "
        f"password={password}"
    )


def get_policy_columns() -> list[str]:
    return [field.name for field in fields(PolicyRecord)]


def record_to_row(record: PolicyRecord, columns: list[str]) -> tuple:
    return tuple(getattr(record, column) for column in columns)


def load_policies_to_postgres(
    rows: int,
    chunk_size: int,
    truncate: bool,
) -> None:
    columns = get_policy_columns()

    column_list = ",\n    ".join(columns)

    copy_sql = f"""
        COPY {TABLE_NAME} (
            {column_list}
        )
        FROM STDIN
    """

    connection_string = get_connection_string()

    with psycopg.connect(connection_string) as conn:
        with conn.cursor() as cur:
            if truncate:
                print(f"Truncating {TABLE_NAME}...")
                cur.execute(f"TRUNCATE TABLE {TABLE_NAME};")

            rows_written = 0

            print(f"Loading {rows:,} policy records into {TABLE_NAME}...")

            with cur.copy(copy_sql) as copy:
                while rows_written < rows:
                    current_chunk_size = min(chunk_size, rows - rows_written)

                    batch = PolicyRecordFactory.build_batch(current_chunk_size)

                    for record in batch:
                        copy.write_row(record_to_row(record, columns))

                    rows_written += current_chunk_size

                    print(f"Wrote {rows_written:,} / {rows:,} rows")

        conn.commit()

    print("Load complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic auto policy records and load them directly into Postgres."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=100_000,
        help="Number of policy-term records to generate.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10_000,
        help="Number of records to generate per batch.",
    )

    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate the destination table before loading.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    load_policies_to_postgres(
        rows=args.rows,
        chunk_size=args.chunk_size,
        truncate=args.truncate,
    )


if __name__ == "__main__":
    main()
