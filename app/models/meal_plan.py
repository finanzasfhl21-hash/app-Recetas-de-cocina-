from dataclasses import dataclass

from app.database import get_db

MEAL_TYPES = ["desayuno", "almuerzo", "merienda", "cena"]


@dataclass
class MealPlanEntry:
    id: int
    date: str
    meal_type: str
    recipe_id: int
    recipe_title: str


class MealPlanModel:
    @staticmethod
    def for_range(start_date: str, end_date: str) -> list[MealPlanEntry]:
        rows = (
            get_db()
            .execute(
                """
            SELECT mpe.id, mpe.date, mpe.meal_type, mpe.recipe_id, r.title AS recipe_title
            FROM meal_plan_entries mpe
            JOIN recipes r ON r.id = mpe.recipe_id
            WHERE mpe.date BETWEEN ? AND ?
            ORDER BY mpe.date, mpe.meal_type
            """,
                (start_date, end_date),
            )
            .fetchall()
        )
        return [
            MealPlanEntry(
                id=row["id"],
                date=row["date"],
                meal_type=row["meal_type"],
                recipe_id=row["recipe_id"],
                recipe_title=row["recipe_title"],
            )
            for row in rows
        ]

    @staticmethod
    def for_date(date: str) -> list[MealPlanEntry]:
        return MealPlanModel.for_range(date, date)

    @staticmethod
    def set_entry(date: str, meal_type: str, recipe_id: int) -> int:
        db = get_db()
        db.execute(
            "DELETE FROM meal_plan_entries WHERE date = ? AND meal_type = ?",
            (date, meal_type),
        )
        cursor = db.execute(
            "INSERT INTO meal_plan_entries (date, meal_type, recipe_id) VALUES (?, ?, ?)",
            (date, meal_type, recipe_id),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def delete(entry_id: int) -> None:
        db = get_db()
        db.execute("DELETE FROM meal_plan_entries WHERE id = ?", (entry_id,))
        db.commit()
