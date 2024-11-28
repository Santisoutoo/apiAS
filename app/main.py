# Importamos la librería FastAPI para crear la aplicación web.
from fastapi import FastAPI
from app.supabase_data import SupabaseAPI
# Importamos el router que contiene las rutas relacionadas con los usuarios.
# Importamos las rutas definidas en user_routes.py.
from app.routes.user_routes import user_router
from typing import List, Optional
from pydantic import BaseModel

from fastapi import HTTPException
import json

# Crear la aplicación FastAPI
# FastAPI es un marco de trabajo para construir APIs rápidas con Python 3.7+.
app = FastAPI()

# Incluir el router de 'user_router' que contiene las rutas relacionadas con los usuarios
# `prefix="/api"`: Define un prefijo común para todas las rutas dentro del `user_router`, de manera que todas las rutas definidas en `user_router` tendrán la URL prefijada con `/api`.
# `tags=["Usuarios"]`: Etiqueta las rutas con "Usuarios" para mejorar la organización y visualización en la documentación generada automáticamente por FastAPI (Swagger).
app.include_router(user_router, prefix="/api", tags=["Usuarios"])

# Ruta adicional para la raíz de la aplicación ("/")


@app.get("/")
def read_root():
    """
    Ruta raíz de la API.

    Esta ruta sirve como punto de entrada para la aplicación. 
    Cuando se accede a la URL base (http://localhost:8000/), se devolverá un mensaje de bienvenida.
    """
    return {"message": "Bienvenido a la API de gestión de usuarios"}


class Description(BaseModel):
    DriverNumber: str
    LapTime: Optional[str] = None
    Sector1Time: Optional[str] = None
    Sector2Time: Optional[str] = None
    Sector3Time: Optional[str] = None
    Compound: str
    TyreLife: float
    FreshTyre: bool
    Team: str


class Item(BaseModel):
    id: int
    name: str
    description: Description


class ItemCreate(BaseModel):
    name: str
    description: Description

# Función auxiliar para leer los datos del archivo JSON


def read_data():
    try:
        with open("app/data/data_filtered_pilots.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            # Añadir el índice como id a cada ítem si falta
            for index, item in enumerate(data):
                if 'id' not in item:
                    item['id'] = index
                if 'name' not in item:
                    # Asignar un nombre por defecto si falta
                    item['name'] = f"Item {index}"
            return data
    except FileNotFoundError:
        return []

# Función auxiliar para escribir datos en el archivo JSON


def write_data(data):
    with open("app/data/data_filtered_pilots.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Endpoint para obtener todos los ítems (GET)


@app.get("/items/", response_model=List[Item])
def get_items():
    """
    Devuelve una lista de todos los ítems.
    """
    items = read_data()
    return items

# Endpoint para obtener un ítem específico por su ID (GET)


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    """
    Devuelve un ítem específico basado en su ID.
    """
    items = read_data()
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")


@app.get("/users/supabase", tags=["Usuarios"])
async def get_users_from_supabase():
    """
    Obtiene todos los usuarios desde Supabase usando fetch_data.
    """
    try:
        # Crear instancia de SupabaseAPI
        supabase_client = SupabaseAPI("users", "*")

        # Llamar a fetch_data sin await
        users = supabase_client.fetch_data()

        if not users:
            return {
                "message": "No se encontraron usuarios",
                "data": []
            }

        return {
            "message": "Usuarios obtenidos exitosamente",
            "data": users
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de Supabase: {str(e)}"
        )
