def test_create_employee(client, employee_payload):
    response = client.post("/employees/", json=employee_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == employee_payload["email"]
    assert "id" in data


def test_create_employee_duplicate_email(client, employee_payload):
    client.post("/employees/", json=employee_payload)
    response = client.post("/employees/", json=employee_payload)
    assert response.status_code == 409


def test_create_employee_invalid_email(client, employee_payload):
    employee_payload["email"] = "not-an-email"
    response = client.post("/employees/", json=employee_payload)
    assert response.status_code == 422


def test_create_employee_negative_salary(client, employee_payload):
    employee_payload["salario"] = -100
    response = client.post("/employees/", json=employee_payload)
    assert response.status_code == 422


def test_list_employees_empty(client):
    response = client.get("/employees/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_employees(client, employee_payload):
    client.post("/employees/", json=employee_payload)
    response = client.get("/employees/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_employees_filter_by_puesto(client, employee_payload):
    client.post("/employees/", json=employee_payload)
    second = {**employee_payload, "email": "otro@peopleflow.com", "puesto": "Manager"}
    client.post("/employees/", json=second)

    response = client.get("/employees/?puesto=Engineer")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["puesto"] == "Engineer"


def test_get_employee_by_id(client, employee_payload):
    created = client.post("/employees/", json=employee_payload).json()
    response = client.get(f"/employees/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_employee_not_found(client):
    response = client.get("/employees/000000000000000000000000")
    assert response.status_code == 404


def test_get_employee_invalid_id(client):
    response = client.get("/employees/id-invalido")
    assert response.status_code == 400


def test_update_employee(client, employee_payload):
    created = client.post("/employees/", json=employee_payload).json()
    response = client.put(f"/employees/{created['id']}", json={"salario": 90000.0})
    assert response.status_code == 200
    assert response.json()["salario"] == 90000.0


def test_update_employee_empty_body(client, employee_payload):
    created = client.post("/employees/", json=employee_payload).json()
    response = client.put(f"/employees/{created['id']}", json={})
    assert response.status_code == 422


def test_update_employee_not_found(client):
    response = client.put("/employees/000000000000000000000000", json={"salario": 90000.0})
    assert response.status_code == 404


def test_delete_employee(client, employee_payload):
    created = client.post("/employees/", json=employee_payload).json()
    response = client.delete(f"/employees/{created['id']}")
    assert response.status_code == 204


def test_delete_employee_not_found(client):
    response = client.delete("/employees/000000000000000000000000")
    assert response.status_code == 404


def test_delete_employee_invalid_id(client):
    response = client.delete("/employees/id-invalido")
    assert response.status_code == 400
