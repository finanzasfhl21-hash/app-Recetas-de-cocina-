from dataclasses import dataclass, field

from app.database import get_db


@dataclass
class Category:
    id: int
    name: str
    parent_id: int | None = None
    image_url: str | None = None
    parent_name: str | None = None
    children: list["Category"] = field(default_factory=list)


class CategoryModel:
    @staticmethod
    def all() -> list[Category]:
        rows = (
            get_db()
            .execute(
                """
                SELECT c.id, c.name, c.parent_id, c.image_url, p.name AS parent_name
                FROM categories c
                LEFT JOIN categories p ON p.id = c.parent_id
                ORDER BY COALESCE(p.name, c.name), c.parent_id IS NOT NULL, c.name
                """
            )
            .fetchall()
        )
        return [
            Category(
                id=row["id"],
                name=row["name"],
                parent_id=row["parent_id"],
                image_url=row["image_url"],
                parent_name=row["parent_name"],
            )
            for row in rows
        ]

    @staticmethod
    def top_level() -> list[Category]:
        rows = (
            get_db()
            .execute(
                "SELECT id, name, parent_id, image_url FROM categories "
                "WHERE parent_id IS NULL ORDER BY name"
            )
            .fetchall()
        )
        return [
            Category(
                id=row["id"],
                name=row["name"],
                parent_id=row["parent_id"],
                image_url=row["image_url"],
            )
            for row in rows
        ]

    @staticmethod
    def tree() -> list[Category]:
        rows = (
            get_db()
            .execute(
                "SELECT id, name, parent_id, image_url FROM categories ORDER BY name"
            )
            .fetchall()
        )
        categories = {
            row["id"]: Category(
                id=row["id"],
                name=row["name"],
                parent_id=row["parent_id"],
                image_url=row["image_url"],
            )
            for row in rows
        }
        top_level: list[Category] = []
        for category in categories.values():
            parent = categories.get(category.parent_id) if category.parent_id else None
            if parent is not None:
                parent.children.append(category)
            else:
                top_level.append(category)
        top_level.sort(key=lambda c: c.name)
        for category in categories.values():
            category.children.sort(key=lambda c: c.name)
        return top_level

    @staticmethod
    def get(category_id: int) -> Category | None:
        row = (
            get_db()
            .execute(
                "SELECT id, name, parent_id, image_url FROM categories WHERE id = ?",
                (category_id,),
            )
            .fetchone()
        )
        if row is None:
            return None
        return Category(
            id=row["id"],
            name=row["name"],
            parent_id=row["parent_id"],
            image_url=row["image_url"],
        )

    @staticmethod
    def create(
        name: str, parent_id: int | None = None, image_url: str | None = None
    ) -> int:
        db = get_db()
        cursor = db.execute(
            "INSERT INTO categories (name, parent_id, image_url) VALUES (?, ?, ?)",
            (name, parent_id, image_url),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(
        category_id: int,
        name: str,
        parent_id: int | None = None,
        image_url: str | None = None,
    ) -> None:
        db = get_db()
        db.execute(
            "UPDATE categories SET name = ?, parent_id = ?, image_url = ? WHERE id = ?",
            (name, parent_id, image_url, category_id),
        )
        db.commit()

    @staticmethod
    def delete(category_id: int) -> None:
        db = get_db()
        db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        db.commit()
