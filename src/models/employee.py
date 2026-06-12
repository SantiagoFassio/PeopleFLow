from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class EmployeeCreate(BaseModel):
    """
    Datos requeridos para registrar un nuevo empleado.
    fecha_ingreso es por defecto la fecha y hora actual si no se proporciona.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Santiago",
                "apellido": "Fassio",
                "email": "sfassio@peopleflow.com",
                "puesto": "Fullstack Engineer",
                "salario": 1000.0,
                "fecha_ingreso": "2026-06-01T00:00:00",
            }
        }
    )

    nombre: str
    apellido: str
    email: EmailStr
    puesto: str
    salario: float = Field(..., ge=0, description="Debe ser mayor o igual a 0.")
    fecha_ingreso: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Por defecto se usa la fecha y hora actual (UTC).",
    )


class EmployeeUpdate(BaseModel):
    """
    Datos opcionales para actualizar un empleado existente.
    Solo se modifican los campos que se incluyan en el request.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "puesto": "Fullstack Engineer",
                "salario": 1000.0,
            }
        }
    )

    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    puesto: Optional[str] = None
    salario: Optional[float] = Field(default=None, ge=0)
    fecha_ingreso: Optional[datetime] = None


class EmployeeResponse(BaseModel):
    """
    Representación de un empleado en las respuestas de la API.
    El campo id es el ObjectId de MongoDB convertido a string.
    id es de solo lectura y se genera automáticamente al crear un nuevo empleado. No se puede modificar.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    nombre: str
    apellido: str
    email: EmailStr
    puesto: str
    salario: float
    fecha_ingreso: datetime

    @classmethod
    def from_mongo(cls, doc: dict) -> "EmployeeResponse":
        """
        Convierte un documento de MongoDB a EmployeeResponse.
        MongoDB usa '_id' como clave con tipo ObjectId — este método lo renombra a 'id'
        y lo convierte a string para que sea serializable a JSON.
        """
        doc = dict(doc)
        doc["id"] = str(doc.pop("_id"))
        return cls(**doc)
