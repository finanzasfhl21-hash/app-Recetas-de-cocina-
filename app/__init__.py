from flask import Flask

from app.config import Config
from app.database import register_database


def create_app(config_class: type = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )
    app.config.from_object(config_class)

    register_database(app)

    from app.controllers.category_controller import category_bp
    from app.controllers.home_controller import home_bp
    from app.controllers.planner_controller import planner_bp
    from app.controllers.recipe_controller import recipe_bp
    from app.controllers.shopping_list_controller import shopping_list_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(shopping_list_bp)

    return app
