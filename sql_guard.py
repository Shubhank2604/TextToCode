import re
import sqlite3


def normalize_read_only_sql(raw_sql: str) -> str:
    """Return one read-only SQL statement or reject unsafe model output."""
    sql = raw_sql.strip()
    if sql.startswith("```"):
        sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\s*```$", "", sql)

    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
    if len(statements) != 1:
        raise ValueError("The model must return exactly one SQL statement.")

    sql = statements[0]
    if not re.match(r"^(SELECT|WITH)\b", sql, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are permitted.")

    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|"
        r"VACUUM|REINDEX|ANALYZE|PRAGMA|TRIGGER)\b",
        flags=re.IGNORECASE,
    )
    if forbidden.search(sql):
        raise ValueError("The generated query contains a prohibited operation.")
    return sql


def query_db(raw_sql: str, database_path: str) -> tuple[str, list[tuple], bool]:
    sql = normalize_read_only_sql(raw_sql)
    connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
    try:
        rows = connection.execute(sql).fetchmany(101)
    finally:
        connection.close()
    return sql, rows[:100], len(rows) > 100
