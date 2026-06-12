# PeopleFLow API

API interna de gestión de empleados construida mediante **FastAPI** y **MongoDB**. Incluye reporte automático de salario promedio cada lunes a las 08:00.

## Stack tecnológico

- Python 3.12
- FastAPI: Framework Web
- MongoDB 7.0: Persistencia
- APScheduler: Programación de tareas
- Docker - Docker Compose: Contenedores
- Pydantic v2: Validación de datos

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) >= 20.x
- [Docker Compose](https://docs.docker.com/compose/) >= 2.x
- Para desarrollo local sin Docker: Python 3.12+

## Inicio rápido con Docker

1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd PeopleFLow
```

2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con las credenciales. por defecto esta seteado a usar docker
```

3. Levantar los servicios
```bash
docker compose up --build
```

4. Abrir la documentación interactiva en Swagger
(http://localhost:8000/docs)

## Finalización del entorno con Docker

```bash
docker compose down -v
```

> Nota: Los datos persisten en un volumen Docker (`mongo_data`). Mediante 'docker compose down -v' estos datos se eliminan.

## Desarrollo local (sin Docker)

1. Crear entorno virtual (EN LINUX)
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno (MONGO_URL debe apuntar a localhost:27017)
```bash
cp .env.example .env
# Por defecto el ejemplo usa docker. Cambiar la configuracion siguiendo
# las instrucciones del .env.example
```

4. Iniciar el servidor con uvicorn
```bash
uvicorn src.main:app --reload
```

> Nota: Se tiene en cuenta que se usa docker por defecto. Para que este set de comendos funcione el contendor docker debe estar corriendo (ya que es el que contiene mongo). La alternativa es instalar Mongo localmente

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `MONGO_USER` | Usuario root de MongoDB | `admin` |
| `MONGO_PASSWORD` | Contraseña root de MongoDB | `admin` |
| `MONGO_DB_NAME` | Nombre de la base de datos | `peopleflow` |
| `MONGO_URL` | URI de conexión completa | `mongodb://admin:secret@mongo:27017/peopleflow?authSource=admin` |
| `APP_PORT` | Puerto expuesto por la app | `8000` |

> Nota: En Docker Compose el hostname de MongoDB es `mongo`.

## Referencia de la API

La documentación interactiva (Swagger UI) está disponible en `http://localhost:8000/docs`.  
La documentación alternativa (ReDoc) en `http://localhost:8000/redoc`.

Se recomienda este medio para la revisión de la API.

### Endpoints

| Método | Ruta | Descripción | Codigo para acción exitosa |
|---|---|---|---|
| `POST` | `/employees/` | Registrar nuevo empleado | 201 Created |
| `GET` | `/employees/` | Listar empleados (con filtros y paginación) | 200 OK |
| `GET` | `/employees/{id}` | Obtener empleado por ID | 200 OK |
| `PUT` | `/employees/{id}` | Actualizar datos de empleado | 200 OK |
| `DELETE` | `/employees/{id}` | Eliminar empleado | 204 No Content |
| `GET` | `/reports/salary` | Historial de reportes salariales | 200 OK |

### Filtros y paginación (GET /employees/)

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `puesto` | string | — | Filtrar por puesto exacto |
| `skip` | int | 0 | Registros a omitir |
| `limit` | int | 10 | Máximo de resultados (1–100) |

### Modelo de empleado

```json
{
  "nombre":        "Santiago",
  "apellido":      "Fassio",
  "email":         "sfassio@peopleflow.com",
  "puesto":        "Fullstack Engineer",
  "salario":       75000.0,
  "fecha_ingreso": "2026-06-01T00:00:00"
}
```

## Tarea programada

Cada **lunes a las 08:00** se ejecuta automáticamente un reporte que:

1. Calcula el **promedio de salarios** de todos los empleados.
2. Guarda el resultado en la colección `salary_reports` de MongoDB.
3. Imprime en consola:

```
[SalaryReport] 2026-06-15T08:00:00 — Promedio: $72,500.00 | Empleados: 42
```

## Tests

Los tests usan `pytest` con `mongomock` (MongoDB en memoria) — no requieren ninguna conexión real a la base de datos.

1. Activar el entorno virtual e instalar dependencias (si no se hizo antes)
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

2. Correr los tests
```bash
pytest tests/ -v
```
