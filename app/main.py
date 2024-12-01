# Importamos la librería FastAPI para crear la aplicación web.
from fastapi import FastAPI
from app.supabase_data import SupabaseAPI
# Importamos el router que contiene las rutas relacionadas con los usuarios.


from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from fastapi import HTTPException
import json

# Crear la aplicación FastAPI
# FastAPI es un marco de trabajo para construir APIs rápidas con Python 3.7+.
app = FastAPI()


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


class UserUpdate(BaseModel):
    """Modelo para actualización de usuarios"""
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan",
                "surname": "Pérez",
                "gender": "M",
                "email": "juan@email.com",


            }
        }


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


@app.post("/users/supabase", tags=["Usuarios"])
async def post_users_to_supabase(
    name: str,
    surname: str,
    gender: str,
    email: str,
    password: str,
    nick: str,
    role: str
):
    """
    Inserta un nuevo usuario en la tabla 'users' de Supabase.
    """
    try:
        # Crear instancia de SupabaseAPI
        data_to_insert = {
            "nick": nick,
            "name": name,
            "surname": surname,
            "gender": gender,
            "email": email,
            "password": password,
            "role": role,
        }
        supabase_client = SupabaseAPI(
            tabla="users", select="*", data=data_to_insert)

        # Llamar al método post_data
        response = supabase_client.post_data()

        return {
            "message": "Usuario insertado exitosamente",
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de creación de usuario: {str(e)}"
        )


@app.put("/users/{nick}", tags=["Usuarios"])
async def update_user(nick: str, user_update: UserUpdate):
    try:
        # Solo incluir campos establecidos
        update_data = user_update.model_dump(exclude_unset=True)

        # Crear instancia con datos limpios
        supabase = SupabaseAPI(tabla="users", select="*", data=update_data)
        response = supabase.update_user(nick, update_data)

        return {"message": "Usuario actualizado exitosamente", "data": response.data}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error actualizando usuario: {str(e)}")


@app.delete("/users/{nick}", tags=["Usuarios"])
async def delete_user(nick: str):
    """Endpoint para eliminar usuario"""
    try:
        # Corregimos la instanciación usando SupabaseAPI con los parámetros correctos
        supabase = SupabaseAPI(tabla="users", select="*", data=None)
        response = supabase.delete_user(nick)
        return {"message": "Usuario eliminado exitosamente", "data": response.data}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando usuario: {str(e)}"
        )
