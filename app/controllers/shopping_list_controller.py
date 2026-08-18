from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models.recipe import RecipeModel
from app.models.shopping_list import ShoppingListModel

shopping_list_bp = Blueprint("shopping_list", __name__, url_prefix="/listas-compra")


@shopping_list_bp.route("/")
def list_shopping_lists():
    shopping_lists = ShoppingListModel.all()
    recipes = RecipeModel.all()
    return render_template(
        "shopping_list/list.html", shopping_lists=shopping_lists, recipes=recipes
    )


@shopping_list_bp.route("/generar", methods=["POST"])
def generate():
    name = request.form.get("name", "").strip() or "Lista de la compra"
    week_start = request.form.get("week_start")

    if week_start:
        start = date.fromisoformat(week_start)
        end = start + timedelta(days=6)
        list_id = ShoppingListModel.create_from_range(
            name, start.isoformat(), end.isoformat()
        )
    else:
        recipe_ids = [int(value) for value in request.form.getlist("recipe_ids[]")]
        if not recipe_ids:
            flash("Selecciona al menos una receta.", "error")
            return redirect(
                request.referrer or url_for("shopping_list.list_shopping_lists")
            )
        list_id = ShoppingListModel.create_from_recipe_ids(name, recipe_ids)

    flash("Lista de la compra generada.", "success")
    return redirect(url_for("shopping_list.detail", list_id=list_id))


@shopping_list_bp.route("/<int:list_id>")
def detail(list_id: int):
    shopping_list = ShoppingListModel.get(list_id)
    if shopping_list is None:
        flash("La lista no existe.", "error")
        return redirect(url_for("shopping_list.list_shopping_lists"))
    return render_template("shopping_list/detail.html", shopping_list=shopping_list)


@shopping_list_bp.route("/<int:list_id>/item", methods=["POST"])
def add_item(list_id: int):
    name = request.form.get("name", "").strip()
    unit = request.form.get("unit", "").strip()
    try:
        quantity = float(request.form.get("quantity") or 0)
    except ValueError:
        quantity = 0.0

    if name:
        ShoppingListModel.add_manual_item(list_id, name, quantity, unit)
        flash("Item agregado.", "success")
    else:
        flash("El nombre del item es obligatorio.", "error")
    return redirect(url_for("shopping_list.detail", list_id=list_id))


@shopping_list_bp.route("/<int:list_id>/item/<int:item_id>/toggle", methods=["POST"])
def toggle_item(list_id: int, item_id: int):
    purchased = request.form.get("purchased") == "1"
    ShoppingListModel.set_purchased(item_id, purchased)
    return redirect(url_for("shopping_list.detail", list_id=list_id))


@shopping_list_bp.route("/<int:list_id>/eliminar", methods=["POST"])
def delete(list_id: int):
    ShoppingListModel.delete(list_id)
    flash("Lista eliminada.", "success")
    return redirect(url_for("shopping_list.list_shopping_lists"))
