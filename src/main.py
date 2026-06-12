from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.database import connect_db, close_db
from src.scheduler import start_scheduler, stop_scheduler
from src.routes.employees import router as employees_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Controla el ciclo de vida de la aplicación.

    Todo lo que está ANTES del 'yield' se ejecuta al arrancar:
      - Conecta con MongoDB y crea el índice único de email.
      - Arranca el scheduler del reporte salarial.

    Todo lo que está DESPUÉS del 'yield' se ejecuta al apagar:
      - Detiene el scheduler.
      - Cierra la conexión con MongoDB.
    """
    connect_db()
    start_scheduler()
    yield
    stop_scheduler()
    close_db()


app = FastAPI(
    title="PeopleFLow API",
    description=(
        "API interna de gestión de empleados. "
        "Incluye reporte automático de salario promedio cada lunes a las 08:00."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Registra todas las rutas de empleados bajo el prefijo /employees
app.include_router(employees_router, prefix="/employees", tags=["Empleados"])
