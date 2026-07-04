from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQL_FILE = PROJECT_ROOT / "sql" / "create_policy_terms.sql"


def load_database_settings() -> dict[str, str | int]:
    """
    Load Postgres connection settings from the project-level .env file.
    """

    env_path = PROJECT_ROOT / ".env"
    load_dotenv(env_path)

    settings = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "insurance_pricing"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }

    missing = [key for key, value in settings.items() if value in (None, "")]

    if missing:
        raise ValueError(
            f"Missing required database setting(s): {missing}. "
            f"Check your .env file at: {env_path}"
        )

    return settings


def get_connection_kwargs(dbname: str | None = None) -> dict[str, str | int]:
    """
    Build psycopg connection keyword arguments.
    """

    settings = load_database_settings()

    if dbname is not None:
        settings["dbname"] = dbname

    return settings


def create_database_if_missing() -> None:
    """
    Create the target database if it does not already exist.

    This connects to the default postgres database first because CREATE DATABASE
    cannot run while connected to the database being created.
    """

    target_settings = load_database_settings()
    target_database = str(target_settings["dbname"])

    admin_connection_kwargs = get_connection_kwargs(dbname="postgres")

    with psycopg.connect(**admin_connection_kwargs, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM pg_database
                WHERE datname = %s;
                """,
                (target_database,),
            )

            database_exists = cur.fetchone() is not None

            if database_exists:
                print(f"Database already exists: {target_database}")
                return

            print(f"Creating database: {target_database}")

            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_database))
            )

            print(f"Database created: {target_database}")


def read_sql_file(sql_file: Path) -> str:
    """
    Read a SQL file from disk and return its contents.
    """

    if not sql_file.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_file}\n"
            "Make sure sql/create_policy_terms.sql exists."
        )

    sql_text = sql_file.read_text(encoding="utf-8").strip()

    if not sql_text:
        raise ValueError(f"SQL file is empty: {sql_file}")

    if "\\copy" in sql_text.lower():
        raise ValueError(
            "This bootstrap script can only execute normal SQL. "
            "Remove psql meta-commands like \\copy from the SQL file."
        )

    return sql_text


def create_policy_terms_table(sql_file: Path = DEFAULT_SQL_FILE) -> None:
    """
    Execute sql/create_policy_terms.sql against the target database.

    The SQL file currently drops and recreates synthetic.policy_terms,
    then creates indexes and constraints.
    """

    sql_text = read_sql_file(sql_file)

    target_database = str(load_database_settings()["dbname"])
    connection_kwargs = get_connection_kwargs(dbname=target_database)

    print(f"Running SQL file: {sql_file}")

    with psycopg.connect(**connection_kwargs, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)

    print("Schema/table/index setup complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the Postgres database and bootstrap the policy terms table."
    )

    parser.add_argument(
        "--sql-file",
        type=Path,
        default=DEFAULT_SQL_FILE,
        help="Path to the SQL file used to create the policy terms table.",
    )

    parser.add_argument(
        "--skip-db-create",
        action="store_true",
        help="Skip database creation and only run the SQL bootstrap file.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.skip_db_create:
        create_database_if_missing()

    create_policy_terms_table(sql_file=args.sql_file)


if __name__ == "__main__":
    main()
