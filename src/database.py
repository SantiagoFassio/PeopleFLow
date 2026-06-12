from pymongo import MongoClient
from src.config import settings

_client: MongoClient = None


def connect_db():
    """
    Inicializa la conexión con MongoDB al arrancar la aplicación.

    - Crea el cliente con un timeout de 5 segundos. Si MongoDB no está disponible,
      la app falla.
    - Ejecuta un 'ping' para verificar la conexión.
    - Crea un índice único sobre el campo 'email' en la colección de empleados,
      lo que garantiza a nivel de base de datos que no puede haber dos empleados
      con el mismo email.
    """
    global _client
    _client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
    _client.admin.command("ping")
    col = get_employee_collection()
    col.create_index("email", unique=True)


def close_db():
    """
    Cierra la conexión con MongoDB al apagar la aplicación.
    Se llama desde el lifespan de FastAPI (src/main.py).
    """
    global _client
    if _client:
        _client.close()
        _client = None


def get_employee_collection():
    """
    Retorna la colección 'employees' de MongoDB.
    """
    return _client[settings.mongo_db_name]["employees"]


def get_salary_reports_collection():
    """
    Retorna la colección 'salary_reports' donde se guardan 
    los reportes del scheduler.
    """
    return _client[settings.mongo_db_name]["salary_reports"]