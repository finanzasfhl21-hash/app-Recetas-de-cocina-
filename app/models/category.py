from dataclasses import dataclass

from app.database import get_db


@dataclass
class Category:
    id: int
    name: str


class CategoryModel:
    @staticmethod
    def all() -> list[Category]:
        rows = (
            get_db().execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        )
        return [Category(id=row["id"], name=row["name"]) for row in rows]

    @staticmethod
    def get(category_id: int) -> Category | None:
        row = (
            get_db()
            .execute("SELECT id, name FROM categories WHERE id = ?", (category_id,))
            .fetchone()
        )
        return Category(id=row["id"], name=row["name"]) if row else None

    @staticmethod
    def create(name: str) -> int:
        db = get_db()
        cursor = db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(category_id: int, name: str) -> None:
        db = get_db()
        db.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))
        db.commit()

    @staticmethod
    def delete(category_id: int) -> None:
        db = get_db()
        db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        db.commit()
