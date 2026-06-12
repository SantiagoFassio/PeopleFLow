from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.

    pydantic-settings lee automáticamente las variables del archivo .env
    y las mapea a los campos de esta clase. Si una variable requerida
    no está definida, la app falla al arrancar con un error claro.

    Campos:
    - mongo_url: URI de conexión completa a MongoDB (requerida).
    - mongo_db_name: nombre de la base de datos (por defecto 'peopleflow').
    - app_port: puerto en el que corre la app (por defecto 8000).
    """

    mongo_url: str
    mongo_db_name: str = "peopleflow"
    app_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Ignora variables del .env que no están definidas como campos
        # (ej: MONGO_USER y MONGO_PASSWORD, que usa Docker Compose para
        # inicializar MongoDB pero la app no necesita directamente).
        extra = "ignore"


# Instancia única que se importa en el resto de la app
settings = Settings()
