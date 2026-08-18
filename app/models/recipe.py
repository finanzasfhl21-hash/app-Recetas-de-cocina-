from dataclasses import dataclass, field

from app.database import get_db
from app.models.ingredient import IngredientModel


@dataclass
class RecipeIngredient:
    ingredient_id: int
    name: str
    quantity: float
    unit: str


@dataclass
class Recipe:
    id: int
    title: str
    description: str
    category_id: int | None
    category_name: str | None
    image_url: str | None
    servings: int
    prep_time_minutes: int
    cook_time_minutes: int
    instructions: str
    created_at: str
    updated_at: str
    ingredients: list[RecipeIngredient] = field(default_factory=list)


def _row_to_recipe(row) -> Recipe:
    return Recipe(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        category_id=row["category_id"],
        category_name=row["category_name"],
        image_url=row["image_url"],
        servings=row["servings"],
        prep_time_minutes=row["prep_time_minutes"],
        cook_time_minutes=row["cook_time_minutes"],
        instructions=row["instructions"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class RecipeModel:
    @staticmethod
    def all(search: str | None = None, category_id: int | None = None) -> list[Recipe]:
        db = get_db()
        like = f"%{search}%" if search else None
        rows = db.execute(
            """
            SELECT DISTINCT r.id, r.title, r.description, r.category_id,
                   c.name AS category_name, r.image_url, r.servings, r.prep_time_minutes,
                   r.cook_time_minutes, r.instructions, r.created_at, r.updated_at
            FROM recipes r
            LEFT JOIN categories c ON c.id = r.category_id
            LEFT JOIN recipe_ingredients ri ON ri.recipe_id = r.id
            LEFT JOIN ingredients i ON i.id = ri.ingredient_id
            WHERE (:like IS NULL OR r.title LIKE :like OR i.name LIKE :like)
              AND (
                    :category_id IS NULL
                    OR r.category_id = :category_id
                    OR r.category_id IN (
                        SELECT id FROM categories WHERE parent_id = :category_id
                    )
                  )
            ORDER BY r.title
            """,
            {"like": like, "category_id": category_id},
        ).fetchall()
        return [_row_to_recipe(row) for row in rows]

    @staticmethod
    def recent(limit: int = 5) -> list[Recipe]:
        db = get_db()
        rows = db.execute(
            """
            SELECT r.id, r.title, r.description, r.category_id,
                   c.name AS category_name, r.image_url, r.servings, r.prep_time_minutes,
                   r.cook_time_minutes, r.instructions, r.created_at, r.updated_at
            FROM recipes r
            LEFT JOIN categories c ON c.id = r.category_id
            ORDER BY r.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [_row_to_recipe(row) for row in rows]

    @staticmethod
    def get(recipe_id: int) -> Recipe | None:
        db = get_db()
        row = db.execute(
            """
            SELECT r.id, r.title, r.description, r.category_id,
                   c.name AS category_name, r.image_url, r.servings, r.prep_time_minutes,
                   r.cook_time_minutes, r.instructions, r.created_at, r.updated_at
            FROM recipes r
            LEFT JOIN categories c ON c.id = r.category_id
            WHERE r.id = ?
            """,
            (recipe_id,),
        ).fetchone()
        if row is None:
            return None

        recipe = _row_to_recipe(row)
        ingredient_rows = db.execute(
            """
            SELECT i.id AS ingredient_id, i.name, ri.quantity, ri.unit
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            WHERE ri.recipe_id = ?
            ORDER BY i.name
            """,
            (recipe_id,),
        ).fetchall()
        recipe.ingredients = [
            RecipeIngredient(
                ingredient_id=r["ingredient_id"],
                name=r["name"],
                quantity=r["quantity"],
                unit=r["unit"],
            )
            for r in ingredient_rows
        ]
        return recipe

    @staticmethod
    def _save_ingredients(db, recipe_id: int, ingredients: list[dict]) -> None:
        db.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
        for item in ingredients:
            name = item["name"].strip()
            if not name:
                continue
            ingredient_id = IngredientModel.get_or_create(name)
            db.execute(
                """
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
                VALUES (?, ?, ?, ?)
                """,
                (recipe_id, ingredient_id, item["quantity"], item.get("unit", "")),
            )

    @staticmethod
    def create(data: dict, ingredients: list[dict]) -> int:
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO recipes
                (title, description, category_id, image_url, servings,
                 prep_time_minutes, cook_time_minutes, instructions)
            VALUES (:title, :description, :category_id, :image_url, :servings,
                    :prep_time_minutes, :cook_time_minutes, :instructions)
            """,
            data,
        )
        recipe_id = cursor.lastrowid
        RecipeModel._save_ingredients(db, recipe_id, ingredients)
        db.commit()
        return recipe_id

    @staticmethod
    def update(recipe_id: int, data: dict, ingredients: list[dict]) -> None:
        db = get_db()
        db.execute(
            """
            UPDATE recipes
            SET title = :title,
                description = :description,
                category_id = :category_id,
                image_url = :image_url,
                servings = :servings,
                prep_time_minutes = :prep_time_minutes,
                cook_time_minutes = :cook_time_minutes,
                instructions = :instructions,
                updated_at = datetime('now')
            WHERE id = :id
            """,
            {**data, "id": recipe_id},
        )
        RecipeModel._save_ingredients(db, recipe_id, ingredients)
        db.commit()

    @staticmethod
    def delete(recipe_id: int) -> None:
        db = get_db()
        db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        db.commit()
