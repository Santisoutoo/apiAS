# Importamos las bibliotecas necesarias
from supabase import create_client  # Para interactuar con Supabase.
# Para cargar las variables de entorno desde un archivo .env.
from dotenv import load_dotenv
# Para acceder a las variables de entorno del sistema operativo.
import os

# Cargar las variables del archivo .env
# La ruta relativa se especifica como "../.env", lo que indica que el archivo .env se encuentra en el directorio superior al actual.
load_dotenv(dotenv_path="../.env")

# Obtener las variables de entorno necesarias para la conexión con Supabase.
# Estas variables deben estar definidas en el archivo .env para no ser hardcodeadas.
SUPABASE_URL = os.getenv("SUPABASE_URL")  # La URL de Supabase.
# La clave de API (por ejemplo, clave pública o servicio).
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Crear un cliente para interactuar con Supabase usando las variables de entorno obtenidas.
# La función `create_client` necesita tanto la URL como la clave para poder conectarse correctamente.
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Verificar si las variables de entorno no están definidas.
# Si alguna de las variables esenciales está ausente, se lanzará un error.
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")
