from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY")  # Clave secreta para firmar el JWT
ALGORITHM = os.getenv("ALGORITHM")  # Algoritmo utilizado para firmar el JWT
# Tiempo de expiración del token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Métodos auxiliares


def verify_password(plain_password, hashed_password):
    """Verifica si la contraseña en texto plano coincide con la contraseña encriptada.

    Args:
        plain_password (str): Contraseña proporcionada por el usuario.
        hashed_password (str): Contraseña almacenada en la base de datos.

    Returns:
        bool: True si las contraseñas coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Genera el hash de una contraseña.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Hash de la contraseña.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT.

    Args:
        data (dict): Información a incluir en el token.
        expires_delta (timedelta, optional): Tiempo hasta la expiración del token. Por defecto es 15 minutos.

    Returns:
        str: Token JWT codificado.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15)
                                  )  # Calcula la fecha de expiración
    to_encode.update({"exp": expire})  # Agrega la fecha de expiración al token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY,
                             algorithm=ALGORITHM)  # Codifica el token
    return encoded_jwt

# Dependencia para obtener al usuario actual


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtiene el usuario actual a partir del token proporcionado.

    Args:
        token (str): Token de acceso JWT.

    Raises:
        HTTPException: Si el token es inválido o ha expirado.

    Returns:
        str: Nombre de usuario extraído del token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[
                             ALGORITHM])  # Decodifica el token
        # Obtiene el nombre de usuario del token
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Token inválido o expirado"
        )
