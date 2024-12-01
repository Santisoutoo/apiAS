# Importamos las dependencias necesarias de FastAPI
from fastapi import Depends, HTTPException
# Importamos el cliente de Supabase para interactuar con la base de datos.
from app.supabase_data import SupabaseAPI


# Función para obtener el usuario actual de la base de datos, basado en su 'id_usuario'.
def get_current_user(id_usuario: str):
    """
    Obtiene los detalles de un usuario de la base de datos a partir de su id_usuario.

    Parámetros:
    - id_usuario: ID único del usuario que se busca en la base de datos.

    Retorna:
    - Un diccionario con los datos del usuario si se encuentra.

    Si el usuario no existe, se lanza una excepción HTTP 404.
    """
    # Consulta la tabla 'users' en Supabase, seleccionando todos los campos y filtrando por el 'id_usuario'.
    user = SupabaseAPI.table("users").select(
        "*").eq("id_usuario", id_usuario).execute()

    # Si no se encuentra el usuario, lanzamos una excepción HTTP 404.
    if not user.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si el usuario existe, retornamos sus datos.
    return user.data[0]


# Función para verificar si el usuario tiene el rol de 'admin'.
def admin_required(current_user=Depends(get_current_user)):
    """
    Verifica que el usuario actual tenga el rol de administrador.

    Parámetros:
    - current_user: El usuario actual que se obtiene a través de `get_current_user`.

    Retorna:
    - El usuario actual si tiene el rol de administrador.

    Si el usuario no tiene permisos de administrador, se lanza una excepción HTTP 403.
    """
    # Verificamos si el usuario tiene el rol de 'admin'.
    if current_user["rol"] != "admin":
        # Si no tiene el rol de 'admin', lanzamos una excepción HTTP 403.
        raise HTTPException(
            status_code=403, detail="No tienes permisos de administrador")

    # Si el usuario tiene el rol adecuado, retornamos sus datos.
    return current_user
