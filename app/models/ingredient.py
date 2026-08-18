from dataclasses import dataclass

from app.database import get_db


@dataclass
class Ingredient:
    id: int
    name: str


class IngredientModel:
    @staticmethod
    def all() -> list[Ingredient]:
        rows = (
            get_db()
            .execute("SELECT id, name FROM ingredients ORDER BY name")
            .fetchall()
        )
        return [Ingredient(id=row["id"], name=row["name"]) for row in rows]

    @staticmethod
    def get_or_create(name: str) -> int:
        name = name.strip()
        db = get_db()
        row = db.execute(
            "SELECT id FROM ingredients WHERE name = ?", (name,)
        ).fetchone()
        if row:
            return row["id"]
        cursor = db.execute("INSERT INTO ingredients (name) VALUES (?)", (name,))
        db.commit()
        return cursor.lastrowid
