import os
from supabase import create_client, Client
from dotenv import load_dotenv

class SupabaseAPI:

    def __init__(self, tabla, select):
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

    def fetch_data(self):
        return self.supabase.table(self.tabla).select(self.select).execute()

# Ejemplo de uso
if __name__ == "__main__":
    api = SupabaseAPI("users", "surname")
    response = api.fetch_data()
    print("Datos de la respuesta:", response.data)
    if response.data:
        print("Datos obtenidos de la tabla 'users':")
        for record in response.data:
            print(record)
    else:
        print("No se encontraron registros en la tabla 'users'.")