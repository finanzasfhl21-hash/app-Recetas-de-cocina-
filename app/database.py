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


def init_db(app) -> None:
    db_path = app.config["DATABASE_PATH"]
    if db_path != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_sql = app.config["SCHEMA_PATH"].read_text(encoding="utf-8")
    connection = sqlite3.connect(str(db_path))
    try:
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()


def register_database(app) -> None:
    app.teardown_appcontext(close_db)
    init_db(app)
