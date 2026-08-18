from datetime import date

from flask import Blueprint, render_template

from app.models.meal_plan import MealPlanModel
from app.models.recipe import RecipeModel

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    recent_recipes = RecipeModel.recent(limit=5)
    today = date.today().isoformat()
    today_entries = MealPlanModel.for_date(today)
    return render_template(
        "home.html",
        recent_recipes=recent_recipes,
        today_entries=today_entries,
        today=today,
    )
