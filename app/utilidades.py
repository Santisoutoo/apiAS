import json
from app.fastf1 import sesion


def read_data():
    try:
        with open("app/data/data_filtered_pilots.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            for index, item in enumerate(data):
                if 'id' not in item:
                    item['id'] = index
                if 'name' not in item:
                    item['name'] = f"Item {index}"
            return data
    except FileNotFoundError:
        return []
    
def write_data(data):
    with open("app/data/data_filtered_pilots.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# f1
