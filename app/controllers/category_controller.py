from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from app.models.category import CategoryModel
from app.placeholder import placeholder_svg

category_bp = Blueprint("category", __name__, url_prefix="/categorias")


@category_bp.route("/imagen/<path:name>.svg")
def image_placeholder(name: str):
    return Response(placeholder_svg(name), mimetype="image/svg+xml")


@category_bp.route("/")
def list_categories():
    categories = CategoryModel.tree()
    top_level_categories = CategoryModel.top_level()
    return render_template(
        "categories/list.html",
        categories=categories,
        top_level_categories=top_level_categories,
    )


@category_bp.route("/", methods=["POST"])
def create():
    name = request.form.get("name", "").strip()
    parent_id = request.form.get("parent_id") or None
    image_url = request.form.get("image_url", "").strip() or None
    if name:
        CategoryModel.create(
            name, parent_id=int(parent_id) if parent_id else None, image_url=image_url
        )
        flash("Categoria creada.", "success")
    else:
        flash("El nombre es obligatorio.", "error")
    return redirect(url_for("category.list_categories"))


@category_bp.route("/<int:category_id>/editar", methods=["POST"])
def edit(category_id: int):
    name = request.form.get("name", "").strip()
    parent_id = request.form.get("parent_id") or None
    image_url = request.form.get("image_url", "").strip() or None
    if name:
        CategoryModel.update(
            category_id,
            name,
            parent_id=int(parent_id) if parent_id else None,
            image_url=image_url,
        )
        flash("Categoria actualizada.", "success")
    else:
        flash("El nombre es obligatorio.", "error")
    return redirect(url_for("category.list_categories"))


@category_bp.route("/<int:category_id>/eliminar", methods=["POST"])
def delete(category_id: int):
    CategoryModel.delete(category_id)
    flash("Categoria eliminada.", "success")
    return redirect(url_for("category.list_categories"))
