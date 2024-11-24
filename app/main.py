from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import json
app = FastAPI()

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

# Función auxiliar para leer los datos del archivo JSON
def read_data():
    try:
        with open("app/data/data_filtered_pilots.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            # Añadir el índice como id a cada ítem si falta
            for index, item in enumerate(data):
                if 'id' not in item:
                    item['id'] = index
                if 'name' not in item:
                    item['name'] = f"Item {index}"  # Asignar un nombre por defecto si falta
            return data
    except FileNotFoundError:
        return []

# Función auxiliar para escribir datos en el archivo JSON
def write_data(data):
    with open("app/data/data_filtered_pilots.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Endpoint para obtener todos los ítems (GET)
@app.get("/items/", response_model=List[Item])
def get_items():
    """
    Devuelve una lista de todos los ítems.
    """
    items = read_data()
    return items

# Endpoint para obtener un ítem específico por su ID (GET)
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    """
    Devuelve un ítem específico basado en su ID.
    """
    items = read_data()
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")

# Endpoint para crear un nuevo ítem (POST)
@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate):
    """
    Crea un nuevo ítem y lo guarda en el archivo JSON.
    """
    items = read_data()
    new_item = item.dict()
    new_item["id"] = len(items)  # Asigna un ID único al nuevo ítem
    items.append(new_item)
    write_data(items)
    return new_item