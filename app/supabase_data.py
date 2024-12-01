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
