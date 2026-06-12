from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query, Response, status
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.database import get_employee_collection
from src.models.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate

router = APIRouter()

def _parse_object_id(id: str) -> ObjectId:
    """
    Convierte un string a ObjectId de MongoDB para validar su formato.
    Si el string no tiene el formato válido de un ObjectId (24 caracteres 
    hexadecimales), lanza un 400 Bad Request.
    Usado en la ruta GET /{id}, PUT /{id} y DELETE /{id} para validar el 
    ID antes de consultar la base de datos.
    """
    try:
        return ObjectId(id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Formato de ID inválido")


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(body: EmployeeCreate):
    """
    Registra un nuevo empleado en la base de datos.

    - El email debe ser único. Si ya existe un empleado con el mismo email, retorna 409.
    - El campo 'fecha_ingreso' es la fecha y hora actual (UTC) por defecto.
    - Retorna el empleado creado con su 'id' generado por MongoDB.
    """
    col = get_employee_collection()
    payload = body.model_dump()
    try:
        result = col.insert_one(payload)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Este email ya está registrado")
    doc = col.find_one({"_id": result.inserted_id})
    return EmployeeResponse.from_mongo(doc)


@router.get("/", response_model=List[EmployeeResponse])
def list_employees(
    puesto: Optional[str] = Query(default=None, description="Filtrar por puesto exacto (ej: 'Engineer')"),
    skip: int = Query(default=0, ge=0, description="Cantidad de registros a saltar (para paginación)"),
    limit: int = Query(default=10, ge=1, le=100, description="Máximo de resultados por página (1-100)"),
):
    """
    Devuelve la lista de empleados con soporte de filtrado y paginación.

    - **puesto**: si se provee, filtra por coincidencia exacta con el 
    campo 'puesto'.
    - **skip + limit**: permiten paginar. Por ejemplo, skip=10&limit=10 
    devuelve la segunda página de 10 registros.
    - Si no hay empleados, retorna una lista vacía.
    """
    col = get_employee_collection()
    query_filter = {"puesto": puesto} if puesto else {}
    docs = list(col.find(query_filter).skip(skip).limit(limit))
    return [EmployeeResponse.from_mongo(doc) for doc in docs]


@router.get("/{id}", response_model=EmployeeResponse)
def get_employee(id: str):
    """
    Devuelve un empleado por su ID único.

    - Retorna 400 si el ID no tiene el formato correcto de MongoDB (ObjectId).
    - Retorna 404 si no existe ningún empleado con ese ID.
    """
    col = get_employee_collection()
    oid = _parse_object_id(id)
    doc = col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return EmployeeResponse.from_mongo(doc)


@router.put("/{id}", response_model=EmployeeResponse)
def update_employee(id: str, body: EmployeeUpdate):
    """
    Actualiza los datos de un empleado existente. La actualización es parcial:
    solo se modifican los campos que se incluyan en el body — los demás quedan intactos.

    - Retorna 400 si el ID no tiene el formato correcto de MongoDB (ObjectId).
    - Retorna 404 si no existe ningún empleado con ese ID.
    - Retorna 409 si el nuevo email ya pertenece a otro empleado.
    - Retorna 422 si el body está vacío (ningún campo para actualizar).
    - Retorna el empleado con los datos ya actualizados.
    """
    col = get_employee_collection()
    oid = _parse_object_id(id)
    # Se filtran los campos que vienen None para no sobreescribir los datos existentes
    # Si no hay nada que actualizar (todos los campos son None), se lanza un error 422
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=422, detail="No se proporcionaron campos para actualizar")
    try:
        doc = col.find_one_and_update(
            {"_id": oid},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Este email ya está registrado")
    if not doc:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return EmployeeResponse.from_mongo(doc)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(id: str):
    """
    Elimina un empleado por su ID.

    - Retorna 400 si el ID no tiene el formato correcto de MongoDB (ObjectId).
    - Retorna 404 si no existe ningún empleado con ese ID.
    - Retorna 204 No Content si la eliminación fue exitosa (sin body en la respuesta).
    """
    col = get_employee_collection()
    oid = _parse_object_id(id)
    result = col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
