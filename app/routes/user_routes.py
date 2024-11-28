# Importamos las dependencias necesarias para la API de FastAPI.
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
# Importamos el cliente de SupabaseAPI para interactuar con la base de datos de SupabaseAPI.
from app.supabase_data import SupabaseAPI
# Importamos la función que verifica si el usuario tiene permisos de administrador.
from app.routes.auth import admin_required

# Creamos un router para gestionar las rutas relacionadas con usuarios.
user_router = APIRouter()

# Modelos de datos para validar la información de los usuarios.


class User(BaseModel):
    """
    Modelo Pydantic para la representación de un usuario.
    Utilizado para la salida de datos en las rutas GET y POST.
    """
    id_usuario: str
    nombre: str
    apellido: str
    correo: str
    genero: str
    is_active: bool
    rol: str  # Campo para almacenar el rol del usuario (admin, usuario, etc.)


class UserCreate(BaseModel):
    """
    Modelo Pydantic para la creación de un nuevo usuario.
    Utilizado para la entrada de datos en las rutas POST y PUT.
    """
    id_usuario: str
    nombre: str
    apellido: str
    correo: str
    genero: str
    is_active: bool
    rol: str

# Funciones auxiliares para interactuar con la base de datos de SupabaseAPI.


def fetch_users():
    """
    Obtiene todos los usuarios de la tabla 'users' en SupabaseAPI.

    Retorna:
    - Una lista de usuarios si la consulta es exitosa.
    - Lanza una excepción HTTP 500 si ocurre un error al obtener los usuarios.
    """
    response = SupabaseAPI.table("users").select("*").execute()
    if response.error:
        raise HTTPException(
            status_code=500, detail="Error al obtener usuarios")
    return response.data


def fetch_user_by_id(id_usuario: str):
    """
    Obtiene un usuario específico de la tabla 'users' utilizando su id_usuario.

    Parámetros:
    - id_usuario: El identificador único del usuario a buscar.

    Retorna:
    - Los datos del usuario si la consulta es exitosa.
    - Lanza una excepción HTTP 404 si el usuario no se encuentra.
    """
    response = SupabaseAPI.table("users").select(
        "*").eq("id_usuario", id_usuario).execute()
    if response.error:
        raise HTTPException(status_code=500, detail="Error al obtener usuario")
    if not response.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return response.data[0]


def insert_user(user_data: dict):
    """
    Inserta un nuevo usuario en la tabla 'users' de SupabaseAPI.

    Parámetros:
    - user_data: Los datos del usuario a insertar.

    Lanza una excepción HTTP 500 si ocurre un error al insertar el usuario.
    """
    response = SupabaseAPI.table("users").insert(user_data).execute()
    if response.error:
        raise HTTPException(status_code=500, detail="Error al crear usuario")


def update_user_data(id_usuario: str, updates: dict):
    """
    Actualiza los datos de un usuario en la tabla 'users' utilizando su id_usuario.

    Parámetros:
    - id_usuario: El identificador único del usuario a actualizar.
    - updates: Un diccionario con los datos actualizados del usuario.

    Lanza una excepción HTTP 500 si ocurre un error al actualizar los datos.
    """
    response = SupabaseAPI.table("users").update(
        updates).eq("id_usuario", id_usuario).execute()
    if response.error:
        raise HTTPException(
            status_code=500, detail="Error al actualizar usuario")


def delete_user_from_db(id_usuario: str):
    """
    Elimina un usuario de la tabla 'users' utilizando su id_usuario.

    Parámetros:
    - id_usuario: El identificador único del usuario a eliminar.

    Lanza una excepción HTTP 500 si ocurre un error al eliminar el usuario.
    """
    response = SupabaseAPI.table("users").delete().eq(
        "id_usuario", id_usuario).execute()
    if response.error:
        raise HTTPException(
            status_code=500, detail="Error al eliminar usuario")

# Endpoints para gestionar usuarios.


@user_router.get("/users/", response_model=List[User])
def get_users():
    """
    Ruta GET que obtiene todos los usuarios de la base de datos.

    Retorna:
    - Una lista de objetos 'User' con los datos de todos los usuarios.
    """
    return fetch_users()


@user_router.get("/users/{id_usuario}", response_model=User)
def get_user(id_usuario: str):
    """
    Ruta GET que obtiene un usuario específico por su id_usuario.

    Parámetros:
    - id_usuario: El identificador único del usuario a obtener.

    Retorna:
    - El objeto 'User' con los datos del usuario correspondiente.
    """
    return fetch_user_by_id(id_usuario)


@user_router.post("/users/", response_model=User)
def create_user(user: UserCreate):
    """
    Ruta POST que crea un nuevo usuario en la base de datos.

    Parámetros:
    - user: Un objeto 'UserCreate' con los datos del nuevo usuario.

    Retorna:
    - El objeto 'User' con los datos del usuario recién creado.

    Si el 'id_usuario' ya existe, lanza una excepción HTTP 400.
    """
    # Comprobamos si el usuario ya existe
    existing_user = SupabaseAPI.table("users").select(
        "*").eq("id_usuario", user.id_usuario).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="El id_usuario ya existe")
    insert_user(user.model_dump())  # Insertamos el usuario
    return user


@user_router.put("/users/{id_usuario}", response_model=User)
def update_user(id_usuario: str, updated_user: UserCreate):
    """
    Ruta PUT que actualiza los datos de un usuario existente.

    Parámetros:
    - id_usuario: El identificador único del usuario a actualizar.
    - updated_user: Un objeto 'UserCreate' con los datos actualizados del usuario.

    Retorna:
    - El objeto 'User' con los datos actualizados del usuario.
    """
    fetch_user_by_id(id_usuario)  # Verifica que el usuario exista
    update_user_data(id_usuario, updated_user.model_dump()
                     )  # Actualiza los datos
    return updated_user


@user_router.delete("/users/{id_usuario}")
def delete_user(id_usuario: str):
    """
    Ruta DELETE que elimina un usuario de la base de datos.

    Parámetros:
    - id_usuario: El identificador único del usuario a eliminar.

    Retorna:
    - Un mensaje indicando que el usuario ha sido eliminado exitosamente.
    """
    fetch_user_by_id(id_usuario)  # Verifica que el usuario exista
    delete_user_from_db(id_usuario)  # Elimina el usuario
    return {"message": "Usuario eliminado exitosamente"}


@user_router.post("/users/", response_model=User)
def create_user(user: UserCreate, current_user=Depends(admin_required)):
    """
    Ruta POST para crear un nuevo usuario, solo accesible por administradores.

    Parámetros:
    - user: Un objeto 'UserCreate' con los datos del nuevo usuario.
    - current_user: El usuario actual que debe ser un administrador (dependencia de 'admin_required').

    Retorna:
    - El objeto 'User' con los datos del usuario recién creado.

    Lanza una excepción HTTP 403 si el usuario no es un administrador.
    """
    insert_user(user.model_dump())  # Insertamos el usuario
    return user
