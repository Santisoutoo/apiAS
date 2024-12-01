import os
from supabase import create_client, Client
from dotenv import load_dotenv


class SupabaseAPI():
    def __init__(self, tabla, select, data):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # Obtener la URL de Supabase desde las variables de entorno
        SUPABASE_URL = os.getenv("SUPABASE_URL")

        # Obtener la clave de Supabase desde las variables de entorno
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        # Verificar si las variables de entorno están definidas
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        # Crear el cliente de Supabase utilizando la URL y la clave
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        self.tabla = tabla
        self.select = select
        self.data = data

    def fetch_data(self):
        return self.supabase.table(self.tabla).select(self.select).execute()

    def post_data(self):
        response = (
            self.supabase.table(self.tabla)
            .insert(self.data)
            .execute()
        )
        return response

    # TODO:
    # Crear metodos update y delete para users
    def update_user(self, nick: str, updated_data: dict):
        """Actualiza información del usuario"""
        try:
            # Verificar usuario
            check_user = (
                self.supabase.table(self.tabla)
                .select("*")
                .eq('nick', nick)
                .single()  # Aseguramos que solo obtenemos un registro
                .execute()
            )

            if not check_user.data:
                raise ValueError(
                    f"El usuario {nick} no existe en la base de datos")

            if 'role' in updated_data or 'password' in updated_data:
                raise ValueError(
                    "No se pueden modificar 'role' o 'password' sin autenticación previa")

            # Remover el nick del updated_data si es el mismo que estamos buscando
            if 'nick' in updated_data and updated_data['nick'] == nick:
                del updated_data['nick']

            print(f"Ejecutando UPDATE en tabla {self.tabla}")
            print(f"WHERE nick = {nick}")
            print(f"SET {updated_data}")

            response = (
                self.supabase.table(self.tabla)
                .update(updated_data)
                .eq('nick', nick)
                .execute()
            )

            print(f"Respuesta UPDATE: {response}")

            if not response.data:
                raise ValueError(f"Error al actualizar el usuario {nick}")

            return response

        except Exception as e:
            print(f"Error detallado: {str(e)}")
            raise e

    def delete_user(self, nick: str):
        """Elimina un usuario"""
        try:
            print(f"Intentando eliminar usuario: {nick}")

            response = (
                self.supabase.table(self.tabla)
                .delete()
                .eq('nick', nick)
                .execute()
            )

            print(f"Respuesta completa de delete: {response}")

            if not response.data:
                raise ValueError(
                    f"No se encontró o no se pudo eliminar el usuario {nick}")

            return response
        except Exception as e:
            print(f"Error en delete_user: {str(e)}")
            raise e
