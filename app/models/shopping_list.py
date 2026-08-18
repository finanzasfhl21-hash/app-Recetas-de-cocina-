from dataclasses import dataclass, field

from app.database import get_db


@dataclass
class ShoppingListItem:
    id: int
    ingredient_id: int | None
    name: str
    quantity: float
    unit: str
    purchased: bool


@dataclass
class ShoppingList:
    id: int
    name: str
    created_at: str
    items: list[ShoppingListItem] = field(default_factory=list)


def _aggregate_ingredients(db, recipe_ids: list[int]) -> list[dict]:
    if not recipe_ids:
        return []
    placeholders = ",".join("?" for _ in recipe_ids)
    rows = db.execute(
        f"""
        SELECT ri.ingredient_id, i.name, ri.unit, SUM(ri.quantity) AS total_quantity
        FROM recipe_ingredients ri
        JOIN ingredients i ON i.id = ri.ingredient_id
        WHERE ri.recipe_id IN ({placeholders})
        GROUP BY ri.ingredient_id, ri.unit
        ORDER BY i.name
        """,
        recipe_ids,
    ).fetchall()
    return [
        {
            "ingredient_id": row["ingredient_id"],
            "name": row["name"],
            "quantity": row["total_quantity"],
            "unit": row["unit"],
        }
        for row in rows
    ]


class ShoppingListModel:
    @staticmethod
    def all() -> list[ShoppingList]:
        rows = (
            get_db()
            .execute(
                "SELECT id, name, created_at FROM shopping_lists ORDER BY created_at DESC"
            )
            .fetchall()
        )
        return [
            ShoppingList(id=row["id"], name=row["name"], created_at=row["created_at"])
            for row in rows
        ]

    @staticmethod
    def get(list_id: int) -> ShoppingList | None:
        db = get_db()
        row = db.execute(
            "SELECT id, name, created_at FROM shopping_lists WHERE id = ?", (list_id,)
        ).fetchone()
        if row is None:
            return None

        shopping_list = ShoppingList(
            id=row["id"], name=row["name"], created_at=row["created_at"]
        )
        item_rows = db.execute(
            """
            SELECT sli.id, sli.ingredient_id, sli.custom_name, sli.quantity,
                   sli.unit, sli.purchased, i.name AS ingredient_name
            FROM shopping_list_items sli
            LEFT JOIN ingredients i ON i.id = sli.ingredient_id
            WHERE sli.shopping_list_id = ?
            ORDER BY sli.purchased, COALESCE(i.name, sli.custom_name)
            """,
            (list_id,),
        ).fetchall()
        shopping_list.items = [
            ShoppingListItem(
                id=row["id"],
                ingredient_id=row["ingredient_id"],
                name=row["ingredient_name"] or row["custom_name"],
                quantity=row["quantity"],
                unit=row["unit"],
                purchased=bool(row["purchased"]),
            )
            for row in item_rows
        ]
        return shopping_list

    @staticmethod
    def _create_with_recipe_ids(name: str, recipe_ids: list[int]) -> int:
        db = get_db()
        aggregated = _aggregate_ingredients(db, recipe_ids)
        cursor = db.execute("INSERT INTO shopping_lists (name) VALUES (?)", (name,))
        list_id = cursor.lastrowid
        for item in aggregated:
            db.execute(
                """
                INSERT INTO shopping_list_items
                    (shopping_list_id, ingredient_id, quantity, unit)
                VALUES (?, ?, ?, ?)
                """,
                (list_id, item["ingredient_id"], item["quantity"], item["unit"]),
            )
        db.commit()
        return list_id

    @staticmethod
    def create_from_recipe_ids(name: str, recipe_ids: list[int]) -> int:
        return ShoppingListModel._create_with_recipe_ids(name, recipe_ids)

    @staticmethod
    def create_from_range(name: str, start_date: str, end_date: str) -> int:
        db = get_db()
        rows = db.execute(
            "SELECT DISTINCT recipe_id FROM meal_plan_entries WHERE date BETWEEN ? AND ?",
            (start_date, end_date),
        ).fetchall()
        recipe_ids = [row["recipe_id"] for row in rows]
        return ShoppingListModel._create_with_recipe_ids(name, recipe_ids)

    @staticmethod
    def add_manual_item(list_id: int, name: str, quantity: float, unit: str) -> int:
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO shopping_list_items (shopping_list_id, custom_name, quantity, unit)
            VALUES (?, ?, ?, ?)
            """,
            (list_id, name, quantity, unit),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def set_purchased(item_id: int, purchased: bool) -> None:
        db = get_db()
        db.execute(
            "UPDATE shopping_list_items SET purchased = ? WHERE id = ?",
            (1 if purchased else 0, item_id),
        )
        db.commit()

    @staticmethod
    def delete(list_id: int) -> None:
        db = get_db()
        db.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))
        db.commit()
