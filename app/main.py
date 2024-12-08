from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.routes.oauth import get_current_user, create_access_token, verify_password, get_password_hash
from app.supabase_data import SupabaseAPI
from typing import List, Optional, Dict
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")  # URL de Supabase
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Clave de la API de Supabase
# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Crear la aplicación FastAPI
app = FastAPI()


@app.get("/")
def read_root():
    """
    Ruta raíz de la API.

    Cuando se accede a la URL base (http://localhost:8000/), se devuelve un mensaje de bienvenida.
    """
    return {"message": "Bienvenido a la API de gestión de usuarios"}

# Clases Pydantic para ítems y usuarios


class Description(BaseModel):
    """Modelo para la descripción detallada de un ítem."""
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
    """Modelo para un ítem que incluye id, nombre y descripción."""
    id: int
    name: str
    description: Description


class ItemCreate(BaseModel):
    """Modelo para la creación de un nuevo ítem."""
    name: str
    description: Description


class UserUpdate(BaseModel):
    """Modelo para actualizar los datos de un usuario."""
    nick: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None

# Funciones auxiliares para manejo de JSON


def read_data():
    """
    Lee los datos desde un archivo JSON y los procesa.

    Returns:
        list: Lista de ítems con id y nombre asignados si no existen.
    """
    try:
        with open("app/data/data_filtered_pilots.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            for index, item in enumerate(data):
                if 'id' not in item:
                    item['id'] = index
                if 'name' not in item:
                    item['name'] = f"Item {index}"
            return data
    except FileNotFoundError:
        return []


def write_data(data):
    """
    Escribe los datos en un archivo JSON.

    Args:
        data (list): Lista de ítems a escribir.
    """
    with open("app/data/data_filtered_pilots.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


@app.post("/register")
def register_user(
    nick: str,
    name: str,
    surname: str,
    gender: str,
    email: str,
    password: str
):
    """
    Endpoint para registrar nuevos usuarios.

    Args:
        nick (str): Apodo del usuario.
        name (str): Nombre del usuario.
        surname (str): Apellido del usuario.
        gender (str): Género del usuario.
        email (str): Correo electrónico del usuario.
        password (str): Contraseña del usuario.

    Returns:
        dict: Mensaje de confirmación.
    """
    hashed_password = get_password_hash(
        password)  # Generar hash de la contraseña
    response = supabase.table("users").insert({
        "nick": nick,
        "name": name,
        "surname": surname,
        "gender": gender,
        "email": email,
        "password": hashed_password,
    }).execute()

    print(response)  # Imprimir respuesta para depuración
    return {"message": "¡USUARIO CREADO EXITOSAMENTE!"}


@app.post("/token", response_model=None)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Crea un token de acceso para autenticación.

    Args:
        form_data (OAuth2PasswordRequestForm): Datos del formulario de inicio de sesión.

    Raises:
        HTTPException: Si las credenciales son inválidas.

    Returns:
        dict: Token de acceso y tipo de token.
    """
    response = supabase.table("users").select(
        "*").eq("nick", form_data.username).execute()
    user = response.data[0] if response.data else None
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    """
    Obtiene los datos del usuario actual autenticado.

    Args:
        current_user (str): Correo electrónico del usuario actual.

    Raises:
        HTTPException: Si el usuario no es encontrado.

    Returns:
        dict: Datos del usuario actual.
    """
    response = supabase.table("users").select(
        "*").eq("email", current_user).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return response.data[0]

# Operaciones relacionadas con usuarios desde Supabase


@app.get("/users/supabase", tags=["Usuarios"])
async def get_users_from_supabase(current_user: str = Depends(get_current_user)):
    """
    Devuelve todos los usuarios almacenados en Supabase.

    Args:
        current_user (str): Correo electrónico del usuario actual.

    Raises:
        HTTPException: Si ocurre un error al obtener los datos.

    Returns:
        dict: Mensaje y lista de usuarios.
    """
    try:
        supabase_client = SupabaseAPI("users", "*")
        users = supabase_client.fetch_data()
        if not users:
            return {"message": "No se encontraron usuarios", "data": []}
        return {"message": "Usuarios obtenidos exitosamente", "data": users}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener datos de Supabase: {str(e)}")


@app.put("/users/{email}", tags=["Usuarios"])
async def update_user(email: str, user_update: UserUpdate, current_user: str = Depends(get_current_user)):
    """
    Actualiza un usuario existente.

    Args:
        email (str): Correo electrónico del usuario a actualizar.
        user_update (UserUpdate): Datos a actualizar.
        current_user (str): Correo electrónico del usuario actual.

    Raises:
        HTTPException: Si no se proporcionan datos o si ocurre un error.

    Returns:
        dict: Mensaje y datos actualizados.
    """
    try:
        update_data = {k: v for k, v in user_update.dict().items()
                       if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=400, detail="No se proporcionaron datos para actualizar")
        supabase_client = SupabaseAPI(
            tabla="users", select="*", data=update_data)
        response = supabase_client.update_user(email, update_data)
        return {"message": "Usuario actualizado exitosamente", "data": response.data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error actualizando usuario: {str(e)}")


@app.delete("/users/{nick}", tags=["Usuarios"])
async def delete_user(nick: str, current_user: str = Depends(get_current_user)):
    """
    Elimina un usuario especificado por su nick.

    Args:
        nick (str): Apodo del usuario a eliminar.
        current_user (str): Correo electrónico del usuario actual.

    Raises:
        HTTPException: Si ocurre un error durante la eliminación.

    Returns:
        dict: Mensaje de confirmación y datos de la operación.
    """
    try:
        supabase_client = SupabaseAPI(tabla="users", select="*")
        response = supabase_client.delete_user(nick)
        return {"message": f"Usuario {nick} eliminado exitosamente", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
