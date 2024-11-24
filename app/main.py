# Importamos la librería FastAPI para crear la aplicación web.
from fastapi import FastAPI

# Importamos el router que contiene las rutas relacionadas con los usuarios.
# Importamos las rutas definidas en user_routes.py.
from app.routes.user_routes import user_router

# Crear la aplicación FastAPI
# FastAPI es un marco de trabajo para construir APIs rápidas con Python 3.7+.
app = FastAPI()

# Incluir el router de 'user_router' que contiene las rutas relacionadas con los usuarios
# `prefix="/api"`: Define un prefijo común para todas las rutas dentro del `user_router`, de manera que todas las rutas definidas en `user_router` tendrán la URL prefijada con `/api`.
# `tags=["Usuarios"]`: Etiqueta las rutas con "Usuarios" para mejorar la organización y visualización en la documentación generada automáticamente por FastAPI (Swagger).
app.include_router(user_router, prefix="/api", tags=["Usuarios"])

# Ruta adicional para la raíz de la aplicación ("/")


@app.get("/")
def read_root():
    """
    Ruta raíz de la API.

    Esta ruta sirve como punto de entrada para la aplicación. 
    Cuando se accede a la URL base (http://localhost:8000/), se devolverá un mensaje de bienvenida.
    """
    return {"message": "Bienvenido a la API de gestión de usuarios"}
