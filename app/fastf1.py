import fastf1
import pandas as pd
import json


class sesion():
    """Clase que representa una sesión de F1 y permite cargar, filtrar y exportar datos."""

    def __init__(self, year, circuit, session, drivers):
        """Inicializa la sesión con el año, circuito, tipo de sesión y pilotos.

        Args:
            year (int): Año de la sesión.
            circuit (str): Nombre del circuito.
            session (str): Tipo de sesión (FP1, FP2, FP3, Q, R).
            drivers (list): Lista de códigos de los pilotos.
        """
        self.year: int = year
        self.circuit: str = circuit
        self.session: str = session
        self.drivers: list = drivers
        self.session_data: pd.DataFrame = None  # Datos completos de la sesión
        self.data_filtered_pilots: pd.DataFrame = None  # Datos filtrados por piloto

    def __str__(self):
        """Representación en cadena de la sesión."""
        return f'Cargando la sesión {self.session} del año {self.year}'

    async def load_sesion(self):
        """Carga la sesión especificada por el usuario utilizando la biblioteca fastf1."""
        carga_sesion = fastf1.get_session(
            self.year,
            self.circuit,
            self.session
        )
        carga_sesion.load()  # Carga los datos de la sesión

        if carga_sesion.laps is not None:
            # Si hay vueltas registradas, las almacenamos en session_data
            self.session_data = carga_sesion.laps.reset_index()
        else:
            # Si no hay vueltas, asignamos un DataFrame vacío
            self.session_data = pd.DataFrame()
        print("Contenido de `session_data`:", self.session_data)

    async def filter_by_driver(self):
        """Filtra las vueltas por los nombres de los pilotos especificados."""
        if self.session_data is not None and not self.session_data.empty:
            # Filtrar las vueltas por los pilotos
            self.data_filtered_pilots = self.session_data[self.session_data['Driver'].isin(
                self.drivers)]
            # Resetear el índice
            self.data_filtered_pilots.reset_index(drop=True, inplace=True)
<<<<<<< HEAD
            print("Contenido de `data_filtered_pilots`:",
                  self.data_filtered_pilots)
=======

            # Manejar NaN y valores infinitos
            self.data_filtered_pilots = self.data_filtered_pilots.fillna(0)  # Reemplaza NaN con 0
            self.data_filtered_pilots = self.data_filtered_pilots.replace(
                [float('inf'), float('-inf')], 0)  # Reemplaza valores infinitos con 0
            print("Contenido de `SesionState.data_filtered_pilots`:",
                self.data_filtered_pilots)
>>>>>>> testSanti
        else:
            print("Error: Los datos de la sesión no están disponibles. Asegúrate de ejecutar `load_sesion` primero.")

    async def _drop_tables(self):
        """Elimina columnas innecesarias del DataFrame `data_filtered_pilots`."""
        variables_to_drop = [
            'Sector1SessionTime',
            'Sector2SessionTime',
            'Sector3SessionTime',
            'LapStartTime',
            'LapStartDate',
        ]

        if self.data_filtered_pilots is not None and not self.data_filtered_pilots.empty:
            self.data_filtered_pilots.drop(
                columns=variables_to_drop, inplace=True, errors='ignore')
            print("Columnas eliminadas:", variables_to_drop)
        else:
            print("Error: No hay datos filtrados disponibles para modificar. Asegúrate de ejecutar `filter_by_driver` primero.")

    async def _change_units(self):
        """Convierte las unidades de tiempo de milisegundos a minutos y segundos."""
        variables_to_change = [
            'Time', 'LapTime',
            'Sector1Time', 'Sector2Time', 'Sector3Time'
        ]

        if self.data_filtered_pilots is not None and not self.data_filtered_pilots.empty:
            for var in variables_to_change:
                self.data_filtered_pilots[var] = self.data_filtered_pilots[var].apply(
                    lambda x: f"{int(x.total_seconds(
                    ) // 60)}:{x.total_seconds() % 60:.3f}" if pd.notnull(x) else None
                )
            print("Unidades de tiempo cambiadas a minutos y segundos para las variables:",
                  variables_to_change)
        else:
            print("Error: No hay datos filtrados disponibles para modificar. Asegúrate de ejecutar `filter_by_driver` primero.")

    async def data_to_json(self):
        """Convierte `data_filtered_pilots` a JSON y lo guarda en un archivo."""
        if self.data_filtered_pilots is not None and not self.data_filtered_pilots.empty:
            # Eliminar columnas innecesarias
            await self._drop_tables()
            # Cambiar las unidades de tiempo
            await self._change_units()

            # Convertir a JSON con la estructura especificada
            json_data = self.data_filtered_pilots.apply(
                lambda row: {
                    "id": row.name,
                    "name": row['Driver'],
                    "description": {
                        "DriverNumber": row['DriverNumber'],
                        "LapTime": row['LapTime'] if pd.notnull(row['LapTime']) else None,
                        "Sector1Time": row['Sector1Time'] if pd.notnull(row['Sector1Time']) else None,
                        "Sector2Time": row['Sector2Time'] if pd.notnull(row['Sector2Time']) else None,
                        "Sector3Time": row['Sector3Time'] if pd.notnull(row['Sector3Time']) else None,
                        "Compound": row['Compound'],
                        "TyreLife": row['TyreLife'],
                        "FreshTyre": row['FreshTyre'],
                        "Team": row['Team']
                    }
                }, axis=1
            ).tolist()

            # Guardar el archivo JSON
            with open("data/data_filtered_pilots.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            print("Archivo JSON guardado en: app/data/data_filtered_pilots.json")
        else:
<<<<<<< HEAD
            print("Error: No hay datos filtrados disponibles para guardar. Asegúrate de ejecutar `filter_by_driver` primero.")


def get_user_input():
    """Solicita al usuario que introduzca los detalles de la sesión."""
    year = int(input("Introduce el año de la sesión: "))
    circuit = input("Introduce el circuito de la sesión: ")
    session = input("Introduce el tipo de sesión (FP1, FP2, FP3, Q, R): ")
    drivers = input(
        "Introduce los códigos de los pilotos separados por comas (ej. VER,LEC,HAM): "
    ).split(',')
    return year, circuit, session, drivers


async def main():
    """Función principal para cargar, filtrar y guardar datos de la sesión."""
    year, circuit, session, drivers = get_user_input()
    f1 = sesion(year, circuit, session, drivers)
    await f1.load_sesion()
    await f1.filter_by_driver()
    await f1.data_to_json()

# Ejecutar la función principal
asyncio.run(main())
=======
            print("Error: No hay datos filtrados disponibles para guardar. Asegúrate de ejecutar `filter_by_driver` primero.")
>>>>>>> testSanti
