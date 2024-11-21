from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import json
from typing import List
from enum import Enum

app = FastAPI()


class User(BaseModel):
    id_usuario: str
    nombre: str
    apellido: str
    genero: str
    correo: str
    is_active: bool = True


class UserCreate(BaseModel):
    id_usuario: str
    nombre: str
    apellido: str
    genero: str
    correo: str
    is_active: bool = True

    @validator('correo')
    def validar_correo(cls, v):
        if '@' not in v:
            raise ValueError('Debe ser un correo válido')
        return v

    @validator('genero')
    def validar_genero(cls, v):
        if v.lower() not in ['m', 'f', 'otro']:
            raise ValueError('Género debe ser M, F u Otro')
        return v.lower()


def read_data():
    try:
        with open("app/data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def write_data(data):
    with open("app/data.json", "w") as file:
        json.dump(data, file, indent=4)


@app.get("/users/", response_model=List[User])
def get_users():
    """
    Obtiene la lista de todos los usuarios registrados.
    """
    users = read_data()
    return users


@app.get("/users/{id_usuario}", response_model=User)
def get_user(id_usuario: str):
    """
    Obtiene un usuario específico por su ID.

    Parámetros:
    - id_usuario: Identificador único del usuario
    """
    users = read_data()
    for user in users:
        if user["id_usuario"] == id_usuario:
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    """
    Crea un nuevo usuario en el sistema.

    Parámetros:
    - user: Datos del usuario a crear
    """
    users = read_data()
    if any(u["id_usuario"] == user.id_usuario for u in users):
        raise HTTPException(status_code=400, detail="El id_usuario ya existe")
    new_user = user.dict()
    users.append(new_user)
    write_data(users)
    return new_user


@app.put("/users/{id_usuario}", response_model=User)
def update_user(id_usuario: str, updated_user: UserCreate):
    """
    Actualiza los datos de un usuario existente.

    Parámetros:
    - id_usuario: ID del usuario a actualizar
    - updated_user: Nuevos datos del usuario
    """
    users = read_data()
    for index, user in enumerate(users):
        if user["id_usuario"] == id_usuario:
            users[index] = updated_user.dict()
            write_data(users)
            return users[index]
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.patch("/users/{id_usuario}/estado")
def update_user_status(id_usuario: str, is_active: bool):
    """
    Actualiza el estado de un usuario (activo/inactivo).

    Parámetros:
    - id_usuario: ID del usuario
    - is_active: Nuevo estado del usuario
    """
    users = read_data()
    for index, user in enumerate(users):
        if user["id_usuario"] == id_usuario:
            users[index]["is_active"] = is_active
            write_data(users)
            return {"message": f"Estado del usuario actualizado a: {'activo' if is_active else 'inactivo'}"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.delete("/users/{id_usuario}")
def delete_user(id_usuario: str):
    """
    Elimina un usuario del sistema.

    Parámetros:
    - id_usuario: Identificador único del usuario a eliminar
    """
    users = read_data()
    for index, user in enumerate(users):
        if user["id_usuario"] == id_usuario:
            deleted_user = users.pop(index)
            write_data(users)
            return {
                "message": "Usuario eliminado exitosamente",
                "usuario": f"{deleted_user['nombre']} {deleted_user['apellido']}"
            }
    raise HTTPException(
        status_code=404,
        detail=f"Usuario con ID {id_usuario} no encontrado"
    )
