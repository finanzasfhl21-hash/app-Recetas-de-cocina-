from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models.meal_plan import MEAL_TYPES, MealPlanModel
from app.models.recipe import RecipeModel

planner_bp = Blueprint("planner", __name__, url_prefix="/planificador")

WEEKDAY_NAMES = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado",
    "Domingo",
]
MEAL_TYPE_LABELS = {
    "desayuno": "Desayuno",
    "almuerzo": "Almuerzo",
    "merienda": "Merienda",
    "cena": "Cena",
}


def _week_start(anchor: date) -> date:
    return anchor - timedelta(days=anchor.weekday())


def _parse_anchor(value: str | None) -> date:
    if value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    return date.today()


@planner_bp.route("/")
def week():
    anchor = _parse_anchor(request.args.get("semana"))
    start = _week_start(anchor)
    days = [start + timedelta(days=i) for i in range(7)]
    end = days[-1]

    entries = MealPlanModel.for_range(start.isoformat(), end.isoformat())
    grid: dict[str, dict[str, object]] = {
        day.isoformat(): {meal_type: None for meal_type in MEAL_TYPES} for day in days
    }
    for entry in entries:
        grid[entry.date][entry.meal_type] = entry

    day_info = [
        {"date": day.isoformat(), "label": WEEKDAY_NAMES[day.weekday()]} for day in days
    ]

    return render_template(
        "planner/week.html",
        days=day_info,
        meal_types=MEAL_TYPES,
        meal_type_labels=MEAL_TYPE_LABELS,
        grid=grid,
        recipes=RecipeModel.all(),
        week_start=start.isoformat(),
        prev_week=(start - timedelta(days=7)).isoformat(),
        next_week=(start + timedelta(days=7)).isoformat(),
    )


@planner_bp.route("/asignar", methods=["POST"])
def assign():
    entry_date = request.form.get("date")
    meal_type = request.form.get("meal_type")
    recipe_id = request.form.get("recipe_id")
    semana = request.form.get("semana")

    if entry_date and meal_type in MEAL_TYPES and recipe_id:
        MealPlanModel.set_entry(entry_date, meal_type, int(recipe_id))
        flash("Receta asignada al plan.", "success")
    else:
        flash("Selecciona una receta valida.", "error")

    return redirect(url_for("planner.week", semana=semana))


@planner_bp.route("/quitar/<int:entry_id>", methods=["POST"])
def remove(entry_id: int):
    semana = request.form.get("semana")
    MealPlanModel.delete(entry_id)
    flash("Receta quitada del plan.", "success")
    return redirect(url_for("planner.week", semana=semana))
