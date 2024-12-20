import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.params import Path
from fastapi.security import OAuth2PasswordRequestForm
from supabase import create_client

from app.fastf1 import sesion
from app.models import *
from app.routes.oauth import (
    get_current_user, 
    create_access_token, 
    verify_password, 
    get_password_hash, 
    verify_admin_role
)
from app.supabase_data import SupabaseAPI
from app.supabase_races import SupabaseDataCircuit


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

                        ########################
                        #        FAST F1       #
                        ########################

                                #######
                                #     #
                                # GET #
                                #     #
                                ####### 

@app.get("/f1/session", tags=["F1"])
async def get_f1_session(year: int, circuit: str, session: str, drivers: str):
    """
    Endpoint para obtener datos de una sesión de Fórmula 1.
    """
    try:
        driver_list = drivers.split(',')
        f1_session = sesion(year, circuit, session, driver_list)
        await f1_session.load_sesion()
        await f1_session.filter_by_driver()

        # Validar si hay datos después del filtro
        if f1_session.data_filtered_pilots is not None and not f1_session.data_filtered_pilots.empty:
            # Limpieza adicional del DataFrame
            clean_data = f1_session.data_filtered_pilots.fillna(0).replace(
                [float('inf'), float('-inf')], 0
            )
            return {
                "message": "Datos obtenidos exitosamente",
                "data": clean_data.to_dict(orient="records"),
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron datos para los pilotos especificados ({', '.join(driver_list)}). Verifica el nombre del piloto o los parámetros de la sesión."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al cargar los datos de la sesión: {str(e)}"
        )
    
@app.get("/f1/circuitos/campos", tags=["F1"])
def get_custom_fields_for_circuits(
    circuito: Optional[str] = Query(None, description="Nombre del circuito"),
    fields: Optional[List[str]] = Query(None, description="Campos deseados")
):
    """
    Endpoint para obtener datos personalizados de un circuito basado en los campos solicitados.
    """
    try:
        # Inicializar conexión a Supabase
        supabase_circuit = SupabaseDataCircuit(tabla="datos_circuitos", select="*")
        response = supabase_circuit.fetch_data()

        if not response.data:
            raise HTTPException(status_code=404, detail="No se encontraron datos de circuitos.")

        # Filtrar por circuito si está definido
        circuitos = response.data
        if circuito:
            circuitos = [c for c in circuitos if c.get("circuito") == circuito]

        if not circuitos:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el circuito {circuito}.")

        # Si se solicitan campos específicos, filtrar los datos
        if fields:
            circuitos = [
                {key: c[key] for key in fields if key in c} for c in circuitos
            ]

        return {
            "message": "Datos obtenidos exitosamente",
            "data": circuitos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")




                        ########################
                        # OPERACIONES SUPABASE #
                        ########################
                                #######
                                #     #
                                # GET #
                                #     #
                                #######     


@app.get("/users/me", tags=["Usuarios"])
def read_users_me(current_user: str = Depends(get_current_user), tags=["Usuarios"]):

    response = supabase.table("users").select("*").eq("email", current_user).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return response.data[0]

# Operaciones relacionadas con usuarios desde Supabase
@app.get("/users/supabase", tags=["Usuarios"])
async def get_niks_from_supabase(current_user: str = Depends(get_current_user)):
    """
    Devuelve todos los nick de la base de datos
    """
    try:
        supabase_client = SupabaseAPI("users", "nick")
        users = supabase_client.fetch_data()
        if not users:
            return {"message": "No se encontraron usuarios", "data": []}
        return {"message": "Usuarios obtenidos exitosamente", "data": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de Supabase: {str(e)}")



                                #######
                                #     #
                                # PUT #
                                #     #
                                #######  

@app.put("/users/{nick}", tags=["Usuarios"])
async def update_user(
    nick: str, user_update: UserUpdate, 
    current_user: str = Depends(get_current_user)
):
    """
    Actualiza la información de un usuario utilizando el nick como identificador único.
    """
    try:
        # Filtra los campos a actualizar y excluye el campo "nick" del formulario
        update_data = {k: v for k, v in user_update.dict().items() if v is not None and k != "nick"}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Conexión a la base de datos
        supabase_client = SupabaseAPI(tabla="users", select="*")
        response = supabase_client.update_user(nick, update_data)

        if not response.data:
            raise HTTPException(status_code=404, detail=f"No se encontró usuario con nick: {nick}")

        # Manipula los datos devueltos para eliminar "nick"
        updated_data = response.data[0]
        updated_data.pop("nick", None)  # Elimina "nick" si existe en el dict

        return {"message": "Usuario actualizado exitosamente", "data": updated_data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando usuario: {str(e)}")



@app.put("/f1/calendar/update/{circuit_name}", tags=["F1"])
def update_f1_calendar(
    circuit_name: str, update_data: RaceData = Body(...), current_user: dict = Depends(verify_admin_role)
):
    """
    Endpoint para actualizar información de un circuito dado su nombre.
    """
    try:
        supabase_circuit = SupabaseDataCircuit(tabla="datos_circuitos")
        response = supabase_circuit.update_circuit_information(circuit_name, update_data.dict())
        return {"message": "Información del circuito actualizada exitosamente", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    



@app.put("/users/change-password", tags=["Usuarios"])
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user),
):
    """
    Endpoint para cambiar la contraseña de un usuario autenticado.
    """
    try:
        # Validar que las contraseñas no sean vacías
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Las contraseñas no pueden estar vacías")

        # Obtener usuario desde la base de datos
        response = supabase.table("users").select("*").eq("email", current_user["sub"]).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user = response.data[0]
        print("Datos del usuario encontrado en la base de datos:", user)

        # Verificar que la contraseña actual es correcta
        if not verify_password(current_password, user.get("password", "")):
            raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

        # Hashear la nueva contraseña
        hashed_password = get_password_hash(new_password)

        # Actualizar contraseña en la base de datos
        update_response = (
            supabase.table("users")
            .update({"password": hashed_password})
            .eq("email", current_user["sub"])
            .execute()
        )

        if not update_response.data:
            raise HTTPException(status_code=500, detail="Error al actualizar la contraseña en la base de datos")

        print("Respuesta de actualización completa:", update_response)
        return {"message": "Contraseña actualizada exitosamente"}

    except Exception as e:
        # Imprimir error para depuración
        print("Error al cambiar la contraseña:", str(e))
        raise HTTPException(status_code=500, detail=f"Error al cambiar la contraseña: {str(e)}")

    
                                    ########
                                    #      #
                                    # POST #
                                    #      #
                                    ########


@app.post("/register", tags=["Usuarios"])
def register_user(
    nick: str,
    name: str,
    surname: str,
    gender: str,
    email: str,
    password: str,
    role:str="user"
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
        "role": role
    }).execute()

    print(response)  # Imprimir respuesta para depuración
    return {"message": "¡USUARIO CREADO EXITOSAMENTE!"}


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    response = supabase.table("users").select("*").eq("nick", form_data.username).execute()
    user = response.data[0] if response.data else None

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    # Asegúrate de incluir el rol al generar el token
    access_token = create_access_token(data={"sub": user["email"], "role": user.get("role")})
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/f1/calendar/new", tags=["F1"])
def add_new_race(race_data: RaceData, current_user: dict = Depends(verify_admin_role)):
    """
    Endpoint para añadir una nueva carrera al calendario de F1.
    """
    try:
        race_data_dict = race_data.dict()
        supabase_circuit = SupabaseDataCircuit(tabla="datos_circuitos")
        response = supabase_circuit.create_race(race_data_dict)
        return {"message": "Carrera añadida exitosamente", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    
                                ##########
                                #        #
                                # DELETE #
                                #        #
                                ##########


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
    
@app.delete("/f1/calendar/delete/{race_name}", tags=["F1"])
def delete_race(race_name: str, current_user: dict = Depends(verify_admin_role)):
    """
    Endpoint para eliminar una carrera del calendario de F1.
    """
    try:
        supabase_circuit = SupabaseDataCircuit(tabla="datos_circuitos")
        response = supabase_circuit.delete_race(race_name)
        return {"message": "Carrera eliminada exitosamente", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
