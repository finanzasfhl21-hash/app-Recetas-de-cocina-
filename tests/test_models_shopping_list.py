from app.models.meal_plan import MealPlanModel
from app.models.recipe import RecipeModel
from app.models.shopping_list import ShoppingListModel
from tests.conftest import make_recipe_data


def test_shopping_list_aggregates_quantities_across_recipes(app):
    with app.app_context():
        recipe_a = RecipeModel.create(
            make_recipe_data(title="Pan"),
            [{"name": "Harina", "quantity": 2, "unit": "kg"}],
        )
        recipe_b = RecipeModel.create(
            make_recipe_data(title="Torta"),
            [{"name": "Harina", "quantity": 1, "unit": "kg"}],
        )

        list_id = ShoppingListModel.create_from_recipe_ids(
            "Compra", [recipe_a, recipe_b]
        )
        shopping_list = ShoppingListModel.get(list_id)

        assert len(shopping_list.items) == 1
        assert shopping_list.items[0].name == "Harina"
        assert shopping_list.items[0].quantity == 3


def test_shopping_list_from_week_range(app):
    with app.app_context():
        recipe_id = RecipeModel.create(
            make_recipe_data(title="Guiso"),
            [{"name": "Papa", "quantity": 5, "unit": "unidad"}],
        )
        MealPlanModel.set_entry("2026-08-17", "almuerzo", recipe_id)

        list_id = ShoppingListModel.create_from_range(
            "Compra semana", "2026-08-17", "2026-08-23"
        )
        shopping_list = ShoppingListModel.get(list_id)

        assert len(shopping_list.items) == 1
        assert shopping_list.items[0].name == "Papa"


def test_manual_item_and_toggle_purchased(app):
    with app.app_context():
        list_id = ShoppingListModel.create_from_recipe_ids("Vacia", [])
        item_id = ShoppingListModel.add_manual_item(
            list_id, "Servilletas", 1, "paquete"
        )

        ShoppingListModel.set_purchased(item_id, True)
        shopping_list = ShoppingListModel.get(list_id)

        assert shopping_list.items[0].purchased is True
