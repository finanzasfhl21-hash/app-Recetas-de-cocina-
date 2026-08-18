import os
import tempfile
from pathlib import Path

import pytest

from app import create_app
from app.config import Config


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    class _TestConfig(Config):
        TESTING = True
        DATABASE_PATH = Path(db_path)

    flask_app = create_app(_TestConfig)

    yield flask_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def make_recipe_data(**overrides) -> dict:
    data = {
        "title": "Receta de prueba",
        "description": "Descripcion",
        "category_id": None,
        "servings": 2,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "instructions": "Paso 1. Paso 2.",
    }
    data.update(overrides)
    return data
