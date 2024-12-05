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
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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
    nick: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None

# Funciones auxiliares para manejo de JSON
def read_data():
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
    endpoint registro usuarios
    """
    hashed_password = get_password_hash(password)
    response = supabase.table("users").insert({
        "nick": nick,
        "name": name,
        "surname": surname,
        "gender": gender,
        "email": email,
        "password": hashed_password,
    }).execute()

    print(response)  # Depurar la estructura de la respuesta
    return {"message": "¡USUARIO CREADO EXITOSAMENTE!"}


@app.post("/token", response_model=None)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Crea token para la autenticación
    """
    response = supabase.table("users").select("*").eq("nick", form_data.username).execute()
    user = response.data[0] if response.data else None
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):

    response = supabase.table("users").select("*").eq("email", current_user).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return response.data[0]



##################################################################################################


# Operaciones relacionadas con usuarios desde Supabase
@app.get("/users/supabase", tags=["Usuarios"])
async def get_users_from_supabase(current_user: str = Depends(get_current_user)):
    """
    Devuelve todos los usuarios de la base de datos
    """
    try:
        supabase_client = SupabaseAPI("users", "*")
        users = supabase_client.fetch_data()
        if not users:
            return {"message": "No se encontraron usuarios", "data": []}
        return {"message": "Usuarios obtenidos exitosamente", "data": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de Supabase: {str(e)}")

# TODO cambiar filtro a por nick

@app.put("/users/{email}", tags=["Usuarios"])
async def update_user(email: str, user_update: UserUpdate, current_user: str = Depends(get_current_user)):
    try:
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        supabase_client = SupabaseAPI(tabla="users", select="*", data=update_data)
        response = supabase_client.update_user(email, update_data)
        return {"message": "Usuario actualizado exitosamente", "data": response.data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando usuario: {str(e)}")

@app.delete("/users/{nick}", tags=["Usuarios"])
async def delete_user(nick: str, current_user: str = Depends(get_current_user)):
    """
    Borra usuario solo si está autenticado
    """
    try:
        supabase_client = SupabaseAPI(tabla="users", select="*")
        response = supabase_client.delete_user(nick)
        return {"message": f"Usuario {nick} eliminado exitosamente", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
