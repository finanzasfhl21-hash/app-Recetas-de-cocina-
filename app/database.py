import sqlite3

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        g.db = sqlite3.connect(str(db_path))
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exception=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _add_missing_columns(
    connection: sqlite3.Connection, table: str, columns_sql: dict[str, str]
) -> None:
    table_exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    if not table_exists:
        return

    existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    for column, definition in columns_sql.items():
        if column not in existing:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")
    connection.commit()


def _migrate_legacy_schema(connection: sqlite3.Connection) -> None:
    _add_missing_columns(
        connection,
        "categories",
        {
            "parent_id": (
                "parent_id INTEGER REFERENCES categories (id) ON DELETE CASCADE"
            ),
            "image_url": "image_url TEXT",
        },
    )
    _add_missing_columns(
        connection, "recipes", {"image_url": "image_url TEXT"}
    )


def init_db(app) -> None:
    db_path = app.config["DATABASE_PATH"]
    if db_path != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_sql = app.config["SCHEMA_PATH"].read_text(encoding="utf-8")
    connection = sqlite3.connect(str(db_path))
    try:
        _migrate_legacy_schema(connection)
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()


def register_database(app) -> None:
    app.teardown_appcontext(close_db)
    init_db(app)
