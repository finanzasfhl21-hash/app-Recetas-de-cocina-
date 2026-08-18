from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models.category import CategoryModel

category_bp = Blueprint("category", __name__, url_prefix="/categorias")


@category_bp.route("/")
def list_categories():
    categories = CategoryModel.all()
    return render_template("categories/list.html", categories=categories)


@category_bp.route("/", methods=["POST"])
def create():
    name = request.form.get("name", "").strip()
    if name:
        CategoryModel.create(name)
        flash("Categoria creada.", "success")
    else:
        flash("El nombre es obligatorio.", "error")
    return redirect(url_for("category.list_categories"))


@category_bp.route("/<int:category_id>/editar", methods=["POST"])
def edit(category_id: int):
    name = request.form.get("name", "").strip()
    if name:
        CategoryModel.update(category_id, name)
        flash("Categoria actualizada.", "success")
    else:
        flash("El nombre es obligatorio.", "error")
    return redirect(url_for("category.list_categories"))


@category_bp.route("/<int:category_id>/eliminar", methods=["POST"])
def delete(category_id: int):
    CategoryModel.delete(category_id)
    flash("Categoria eliminada.", "success")
    return redirect(url_for("category.list_categories"))
