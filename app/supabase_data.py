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
    def update_user(self, email: str, updated_data: dict):
        """
        Actualiza la información de un usuario basándose en su email.
        Args:
            email (str): Email del usuario a actualizar
            updated_data (dict): Datos a actualizar
        Returns:
            Response: Respuesta de Supabase con los datos actualizados
        """
        try:
            print(f"Iniciando actualización para usuario con email: {email}")

            # Verificar usuario existente
            check_user = (
                self.supabase.table(self.tabla)
                .select("*")
                .eq("email", email)
                .execute()
            )

            if not check_user.data:
                raise ValueError(f"No se encontró usuario con email: {email}")

            usuario_actual = check_user.data[0]
            print(f"Usuario encontrado: {usuario_actual}")
            print(f"Aplicando actualización: {updated_data}")

            # Combinar datos actuales con nuevos datos
            datos_actualizados = {**usuario_actual}
            datos_actualizados.update(updated_data)

            # Realizar actualización usando datos combinados
            response = (
                self.supabase.table(self.tabla)
                .update(datos_actualizados)
                .eq("email", email)
                .execute()
            )

            # Verificar actualización
            if not response or not response.data:
                verify = (
                    self.supabase.table(self.tabla)
                    .select("*")
                    .eq("email", email)
                    .execute()
                )
                if verify.data:
                    return verify

            print(f"Actualización completada: {
                  response.data if response.data else 'Verificar datos actualizados'}")
            return response

        except Exception as e:
            print(f"Error en actualización: {str(e)}")
            raise ValueError(f"Error actualizando usuario: {str(e)}")

    def delete_user(self, nick: str):
        try:
            response = (
                self.supabase.table('users')
                .delete()
                .eq('nick', nick)
                .execute()
            )

            if not response.data:
                raise ValueError(f"No se encontró usuario con nick: {nick}")

            print(f"Usuario eliminado: {response.data}")
            return response

        except Exception as e:
            print(f"Error al eliminar usuario: {str(e)}")
            raise ValueError(f"Error eliminando usuario: {str(e)}")
