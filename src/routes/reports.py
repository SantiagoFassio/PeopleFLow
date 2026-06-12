from datetime import datetime
from typing import List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.database import get_salary_reports_collection

router = APIRouter()


class SalaryReportResponse(BaseModel):
    """
    Representa un reporte de salario promedio generado por el scheduler.
    """

    average_salary: float
    employee_count: int
    generated_at: datetime


@router.get("/salary", response_model=List[SalaryReportResponse])
def list_salary_reports(
    skip: int = Query(default=0, ge=0, description="Registros a omitir"),
    limit: int = Query(default=10, ge=1, le=100, description="Máximo de resultados (1-100)"),
):
    """
    Devuelve el historial de reportes de salario promedio generados cada lunes a las 08:00.

    Los reportes se ordenan del más reciente al más antiguo.
    Si aún no se ejecutó ningún reporte, retorna una lista vacía.
    """
    col = get_salary_reports_collection()
    docs = list(col.find({}, {"_id": 0}).sort("generated_at", -1).skip(skip).limit(limit))
    return docs