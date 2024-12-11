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

class RaceData(BaseModel):
    circuito: str
    n_grandes_premios: int
    longitud: float
    vueltas: int
    curvas: int
    distancia: float
    duro: str
    medio: str
    blando: str
    primer_gp: int
