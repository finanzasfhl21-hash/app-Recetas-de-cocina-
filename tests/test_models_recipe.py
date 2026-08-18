from app.models.category import CategoryModel
from app.models.recipe import RecipeModel
from tests.conftest import make_recipe_data


def test_create_and_get_recipe(app):
    with app.app_context():
        category_id = CategoryModel.create("Postres")
        recipe_id = RecipeModel.create(
            make_recipe_data(title="Flan", category_id=category_id),
            [
                {"name": "Huevo", "quantity": 4, "unit": "unidad"},
                {"name": "Leche", "quantity": 1, "unit": "litro"},
            ],
        )

        recipe = RecipeModel.get(recipe_id)

        assert recipe.title == "Flan"
        assert recipe.category_name == "Postres"
        assert len(recipe.ingredients) == 2


def test_search_by_ingredient_name(app):
    with app.app_context():
        RecipeModel.create(
            make_recipe_data(title="Tarta de manzana"),
            [{"name": "Manzana", "quantity": 3, "unit": "unidad"}],
        )
        RecipeModel.create(
            make_recipe_data(title="Sopa"),
            [{"name": "Zanahoria", "quantity": 2, "unit": "unidad"}],
        )

        results = RecipeModel.all(search="Manzana")

        assert len(results) == 1
        assert results[0].title == "Tarta de manzana"


def test_update_recipe_replaces_ingredients(app):
    with app.app_context():
        recipe_id = RecipeModel.create(
            make_recipe_data(title="Ensalada"),
            [{"name": "Lechuga", "quantity": 1, "unit": "unidad"}],
        )

        RecipeModel.update(
            recipe_id,
            make_recipe_data(title="Ensalada mixta"),
            [{"name": "Tomate", "quantity": 2, "unit": "unidad"}],
        )

        recipe = RecipeModel.get(recipe_id)
        assert recipe.title == "Ensalada mixta"
        assert len(recipe.ingredients) == 1
        assert recipe.ingredients[0].name == "Tomate"


def test_delete_recipe(app):
    with app.app_context():
        recipe_id = RecipeModel.create(make_recipe_data(), [])
        RecipeModel.delete(recipe_id)
        assert RecipeModel.get(recipe_id) is None
