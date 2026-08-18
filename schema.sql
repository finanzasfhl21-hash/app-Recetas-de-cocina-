PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories (id) ON DELETE CASCADE,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS recipes (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    title              TEXT NOT NULL,
    description        TEXT NOT NULL DEFAULT '',
    category_id        INTEGER REFERENCES categories (id) ON DELETE SET NULL,
    image_url          TEXT,
    servings           INTEGER NOT NULL DEFAULT 1,
    prep_time_minutes  INTEGER NOT NULL DEFAULT 0,
    cook_time_minutes  INTEGER NOT NULL DEFAULT 0,
    instructions       TEXT NOT NULL DEFAULT '',
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ingredients (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id     INTEGER NOT NULL REFERENCES recipes (id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients (id) ON DELETE CASCADE,
    quantity      REAL NOT NULL,
    unit          TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS meal_plan_entries (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date      TEXT NOT NULL,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('desayuno', 'almuerzo', 'merienda', 'cena')),
    recipe_id INTEGER NOT NULL REFERENCES recipes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shopping_lists (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS shopping_list_items (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    shopping_list_id INTEGER NOT NULL REFERENCES shopping_lists (id) ON DELETE CASCADE,
    ingredient_id    INTEGER REFERENCES ingredients (id) ON DELETE SET NULL,
    custom_name      TEXT,
    quantity         REAL NOT NULL DEFAULT 0,
    unit             TEXT NOT NULL DEFAULT '',
    purchased        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories (parent_id);
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes (category_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients (recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient ON recipe_ingredients (ingredient_id);
CREATE INDEX IF NOT EXISTS idx_meal_plan_date ON meal_plan_entries (date);
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_list ON shopping_list_items (shopping_list_id);
