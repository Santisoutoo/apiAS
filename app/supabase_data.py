import os
from supabase import create_client, Client
from dotenv import load_dotenv


class SupabaseAPI():
    def __init__(self, tabla, select, data=None):
        """
        Inicializa la instancia de SupabaseAPI.

        Args:
            tabla (str): Nombre de la tabla en Supabase.
            select (str): Campos a seleccionar en las consultas.
            data (dict, optional): Datos a insertar o actualizar. Por defecto es None.

        Nota:
            Si no se reciben datos para una operación de inserción o actualización, 'data' debe estar en None.
        """
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # Obtener la URL de Supabase desde las variables de entorno
        SUPABASE_URL = os.getenv("SUPABASE_URL")

        # Obtener la clave de Supabase desde las variables de entorno
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        # Verificar si las variables de entorno están definidas
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL y SUPABASE_KEY deben estar configuradas")

        # Crear el cliente de Supabase utilizando la URL y la clave
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        self.tabla = tabla  # Nombre de la tabla a interactuar
        self.select = select  # Campos a seleccionar en las consultas
        self.data = data  # Datos para operaciones de inserción o actualización

    def fetch_data(self):
        """
        Obtiene datos de la tabla especificada.

        Returns:
            Response: Respuesta de Supabase con los datos obtenidos.
        """
        return self.supabase.table(self.tabla).select(self.select).execute()

    def post_data(self):
        """
        Inserta datos en la tabla especificada.

        Returns:
            Response: Respuesta de Supabase después de la inserción.
        """
        response = (
            self.supabase.table(self.tabla)
            .insert(self.data)
            .execute()
        )
        return response

<<<<<<< HEAD
    def update_user(self, email: str, updated_data: dict):
        """
        Actualiza la información de un usuario basado en su email.

        Args:
            email (str): Email del usuario a actualizar.
            updated_data (dict): Diccionario con los datos a actualizar.

        Returns:
            Response: Respuesta de Supabase con los datos actualizados.

        Raises:
            ValueError: Si no se encuentra el usuario o ocurre un error en la actualización.
        """
        try:
            print(f"Iniciando actualización para usuario con email: {email}")

            # Verificar si el usuario existe
=======
    def update_user(self, nick: str, updated_data: dict):
        """
        Actualiza la información de un usuario basándose en su nick.
        Args:
            nick (str): Nick del usuario a actualizar.
            updated_data (dict): Datos a actualizar.
        Returns:
            Response: Respuesta de Supabase con los datos actualizados.
        """
        try:
            # Verificar usuario existente
>>>>>>> testSanti
            check_user = (
                self.supabase.table(self.tabla)
                .select("*")
                .eq("nick", nick)  # Asegúrate de usar "nick" aquí
                .execute()
            )

            if not check_user.data:
                raise ValueError(f"No se encontró usuario con nick: {nick}")

<<<<<<< HEAD
            usuario_actual = check_user.data[0]
            print(f"Usuario encontrado: {usuario_actual}")
            print(f"Aplicando actualización: {updated_data}")

            # Combinar datos actuales con los nuevos datos
            datos_actualizados = {**usuario_actual}
            datos_actualizados.update(updated_data)

            # Realizar la actualización usando los datos combinados
=======
            # Actualizar los datos del usuario
>>>>>>> testSanti
            response = (
                self.supabase.table(self.tabla)
                .update(updated_data)
                .eq("nick", nick)  # Filtro por "nick"
                .execute()
            )

<<<<<<< HEAD
            # Verificar si la actualización fue exitosa
            if not response or not response.data:
                verify = (
                    self.supabase.table(self.tabla)
                    .select("*")
                    .eq("email", email)
                    .execute()
                )
                if verify.data:
                    return verify
=======
            if not response.data:
                raise ValueError(f"No se pudo actualizar el usuario con nick: {nick}")
>>>>>>> testSanti

            return response
        except Exception as e:
            raise ValueError(f"Error actualizando usuario: {str(e)}")


    def delete_user(self, nick: str):
        """
        Elimina un usuario basado en su nick.

        Args:
            nick (str): Nick del usuario a eliminar.

        Returns:
            Response: Respuesta de Supabase después de la eliminación.

        Raises:
            ValueError: Si no se encuentra el usuario o ocurre un error en la eliminación.
        """
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
