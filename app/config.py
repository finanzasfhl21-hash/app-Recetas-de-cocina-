import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DATABASE_PATH = BASE_DIR / "data" / "recetas.db"
    SCHEMA_PATH = BASE_DIR / "schema.sql"


class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = ":memory:"
