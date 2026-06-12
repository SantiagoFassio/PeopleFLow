import pytest
import mongomock
from unittest.mock import patch
from fastapi.testclient import TestClient

import src.database as db_module
from src.main import app


@pytest.fixture
def client():
    """
    Cliente HTTP para hacer requests a la app en los tests.

    Parchea connect_db, close_db, start_scheduler y stop_scheduler
    para que el lifespan de FastAPI no intente conectarse a MongoDB real
    ni arrancar el scheduler. En su lugar se usa mongomock (MongoDB en memoria).
    Cada test arranca con una base de datos limpia.
    """
    mock_client = mongomock.MongoClient()

    def fake_connect():
        db_module._client = mock_client
        col = db_module.get_employee_collection()
        col.create_index("email", unique=True)

    def fake_close():
        db_module._client = None

    with patch("src.main.connect_db", fake_connect), \
         patch("src.main.close_db", fake_close), \
         patch("src.main.start_scheduler"), \
         patch("src.main.stop_scheduler"):
        with TestClient(app) as c:
            yield c


@pytest.fixture
def employee_payload():
    """Payload base válido para crear un empleado."""
    return {
        "nombre": "Santiago",
        "apellido": "Fassio",
        "email": "sfassio@peopleflow.com",
        "puesto": "Engineer",
        "salario": 75000.0,
        "fecha_ingreso": "2026-06-01T00:00:00",
    }
