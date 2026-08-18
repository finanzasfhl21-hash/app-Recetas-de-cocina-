def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Bienvenido" in response.data


def test_create_category_and_list(client):
    response = client.post(
        "/categorias/", data={"name": "Postre"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Postre" in response.data


def test_create_recipe_via_form(client):
    response = client.post(
        "/recetas/nueva",
        data={
            "title": "Milanesas",
            "description": "Con pure",
            "category_id": "",
            "servings": "4",
            "prep_time_minutes": "15",
            "cook_time_minutes": "20",
            "instructions": "Empanar y freir",
            "ingredient_name[]": ["Carne", "Pan rallado"],
            "ingredient_quantity[]": ["4", "1"],
            "ingredient_unit[]": ["unidad", "taza"],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Milanesas" in response.data
    assert b"Carne" in response.data


def test_recipe_list_page_loads(client):
    response = client.get("/recetas/")
    assert response.status_code == 200


def test_planner_week_page_loads(client):
    response = client.get("/planificador/")
    assert response.status_code == 200


def test_shopping_list_page_loads(client):
    response = client.get("/listas-compra/")
    assert response.status_code == 200
