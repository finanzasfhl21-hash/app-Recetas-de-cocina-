from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from app.models.category import CategoryModel
from app.models.recipe import RecipeModel
from app.placeholder import placeholder_svg

recipe_bp = Blueprint("recipe", __name__, url_prefix="/recetas")


@recipe_bp.route("/imagen/<path:name>.svg")
def image_placeholder(name: str):
    return Response(placeholder_svg(name), mimetype="image/svg+xml")


def _parse_ingredients(form) -> list[dict]:
    names = form.getlist("ingredient_name[]")
    quantities = form.getlist("ingredient_quantity[]")
    units = form.getlist("ingredient_unit[]")

    ingredients = []
    for name, quantity, unit in zip(names, quantities, units):
        name = name.strip()
        if not name:
            continue
        try:
            quantity_value = float(quantity) if quantity else 0.0
        except ValueError:
            quantity_value = 0.0
        ingredients.append(
            {"name": name, "quantity": quantity_value, "unit": unit.strip()}
        )
    return ingredients


def _parse_recipe_form(form) -> dict:
    category_id = form.get("category_id") or None
    return {
        "title": form.get("title", "").strip(),
        "description": form.get("description", "").strip(),
        "category_id": int(category_id) if category_id else None,
        "image_url": form.get("image_url", "").strip() or None,
        "servings": int(form.get("servings") or 1),
        "prep_time_minutes": int(form.get("prep_time_minutes") or 0),
        "cook_time_minutes": int(form.get("cook_time_minutes") or 0),
        "instructions": form.get("instructions", "").strip(),
    }


@recipe_bp.route("/")
def list_recipes():
    search = request.args.get("q") or None
    category_id = request.args.get("category_id")
    category_id = int(category_id) if category_id else None

    recipes = RecipeModel.all(search=search, category_id=category_id)
    categories = CategoryModel.all()
    return render_template(
        "recipes/list.html",
        recipes=recipes,
        categories=categories,
        search=search or "",
        selected_category_id=category_id,
    )


@recipe_bp.route("/<int:recipe_id>")
def detail(recipe_id: int):
    recipe = RecipeModel.get(recipe_id)
    if recipe is None:
        flash("La receta no existe.", "error")
        return redirect(url_for("recipe.list_recipes"))
    return render_template("recipes/detail.html", recipe=recipe)


@recipe_bp.route("/nueva", methods=["GET", "POST"])
def create():
    categories = CategoryModel.all()
    if request.method == "POST":
        data = _parse_recipe_form(request.form)
        ingredients = _parse_ingredients(request.form)
        if not data["title"]:
            flash("El titulo es obligatorio.", "error")
            return render_template(
                "recipes/form.html", recipe=None, categories=categories, form_data=data
            )
        recipe_id = RecipeModel.create(data, ingredients)
        flash("Receta creada correctamente.", "success")
        return redirect(url_for("recipe.detail", recipe_id=recipe_id))

    return render_template(
        "recipes/form.html", recipe=None, categories=categories, form_data=None
    )


@recipe_bp.route("/<int:recipe_id>/editar", methods=["GET", "POST"])
def edit(recipe_id: int):
    recipe = RecipeModel.get(recipe_id)
    if recipe is None:
        flash("La receta no existe.", "error")
        return redirect(url_for("recipe.list_recipes"))

    categories = CategoryModel.all()
    if request.method == "POST":
        data = _parse_recipe_form(request.form)
        ingredients = _parse_ingredients(request.form)
        if not data["title"]:
            flash("El titulo es obligatorio.", "error")
            return render_template(
                "recipes/form.html",
                recipe=recipe,
                categories=categories,
                form_data=data,
            )
        RecipeModel.update(recipe_id, data, ingredients)
        flash("Receta actualizada correctamente.", "success")
        return redirect(url_for("recipe.detail", recipe_id=recipe_id))

    return render_template(
        "recipes/form.html", recipe=recipe, categories=categories, form_data=None
    )


@recipe_bp.route("/<int:recipe_id>/eliminar", methods=["POST"])
def delete(recipe_id: int):
    RecipeModel.delete(recipe_id)
    flash("Receta eliminada.", "success")
    return redirect(url_for("recipe.list_recipes"))
