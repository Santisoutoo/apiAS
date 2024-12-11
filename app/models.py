from pydantic import BaseModel
from typing import Optional

class Description(BaseModel):
    DriverNumber: str
    LapTime: Optional[str] = None
    Sector1Time: Optional[str] = None
    Sector2Time: Optional[str] = None
    Sector3Time: Optional[str] = None
    Compound: str
    TyreLife: float
    FreshTyre: bool
    Team: str


class Item(BaseModel):
    id: int
    name: str
    description: Description


class ItemCreate(BaseModel):
    name: str
    description: Description


class UserUpdate(BaseModel):
    nick: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None

class DataCircuits(BaseModel):
    circuito: Optional[str] = None
    primer_gp: Optional[int] = None
    n_grandes_premios: Optional[int] = None
    longitud: Optional[float] = None
    vueltas: Optional[int] = None
    curvas: Optional[int] = None
    distancia: Optional[float] = None
    duro: Optional[str] = None
    medio: Optional[str] = None
    blando: Optional[str] = None