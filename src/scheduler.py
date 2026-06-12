from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Instancia global del scheduler. Corre en un hilo separado al de FastAPI,
scheduler = BackgroundScheduler()


def generate_salary_report():
    """
    Tarea programada que se ejecuta cada lunes a las 08:00.

    Calcula el promedio de salarios de todos los empleados usando una
    agregación de MongoDB ($group + $avg), guarda el resultado en la
    colección 'salary_reports' e imprime un resumen en consola.

    Si no hay empleados registrados al momento de ejecutarse, omite
    el reporte para evitar guardar un documento sin datos útiles.
    """
    from src.database import get_employee_collection, get_salary_reports_collection

    col = get_employee_collection()
    reports_col = get_salary_reports_collection()

    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_salary": {"$avg": "$salario"},
                "employee_count": {"$sum": 1},
            }
        }
    ]
    results = list(col.aggregate(pipeline))

    if not results:
        print("[SalaryReport] Sin empleados registrados — reporte omitido.")
        return

    avg = results[0]["avg_salary"]
    count = results[0]["employee_count"]
    report = {
        "generated_at": datetime.now(timezone.utc),
        "average_salary": round(avg, 2),
        "employee_count": count,
    }

    reports_col.insert_one(report)
    print(
        f"[SalaryReport] {report['generated_at'].isoformat()} — "
        f"Promedio: ${avg:,.2f} | Empleados: {count}"
    )


def start_scheduler():
    """
    Registra el job del reporte salarial y arranca el scheduler.
    Se llama desde el lifespan de FastAPI (src/main.py) al iniciar la app.
    """
    scheduler.add_job(
        generate_salary_report,
        trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),
        id="weekly_salary_report",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler():
    """
    Detiene el scheduler al apagar la aplicación.
    'wait=False' hace que el shutdown no espere a que terminen los jobs.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)