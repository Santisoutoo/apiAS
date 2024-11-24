import os
from supabase import create_client, Client
from dotenv import load_dotenv

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
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ejecutar la consulta y obtener los resultados
response = supabase.table("users").select("*").execute()

# Depuración adicional
print("Datos de la respuesta:", response.data)

# Verificar y mostrar los resultados
if response.data:
    print("Datos obtenidos de la tabla 'test':")
    for record in response.data:
        print(record)
else:
    print("No se encontraron registros en la tabla 'users'.")