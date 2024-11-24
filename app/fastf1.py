import fastf1
import pandas as pd
import asyncio


class Session():
    """
    Carga una sesión específica del calendario y 
    filtra por pilotos selecionados
    """

    def __init__(self, year, circuit, session, drivers):
        self.year: int = year
        self.circuit: str = circuit
        self.session: str = session
        self.drivers: list = drivers
        self.session_data: pd.DataFrame = None
        self.data_filtered_pilots = None

    def __str__(self):
        return f'Cargando la sesion {self.session} del año {self.year}'

    async def load_sesion(self):
        """
        Carga la sesión especificicada por el usuario
        """
        carga_sesion = fastf1.get_session(
            self.year,
            self.circuit,
            self.session
        )
        carga_sesion.load()

        if carga_sesion.laps is not None:
            self.session_data = carga_sesion.laps.reset_index()  # Si hay vueltas, las asignamos
        else:
            # Si no hay vueltas, asignamos un DataFrame vacío
            self.session_data = pd.DataFrame()
        print("Contenido de `SesionState.session_data`:", self.session_data)

    async def filter_by_driver(self):
        """
        Filtra las vueltas por los nombres de los pilotos seleccionados 
        y reinicia el índice del DataFrame filtrado.
        """
        if self.session_data is not None and not self.session_data.empty:
            # Filtrar las vueltas por los nombres de los pilotos
            self.data_filtered_pilots = self.session_data[
                self.session_data['Driver'].isin(self.drivers)
            ]

            # Imprimir una muestra de los datos filtrados
            print("Contenido de `data_filtered_pilots` después de filtrar:")
            print(self.data_filtered_pilots.head())
        else:
            print(
                "Error: Los datos de la sesión no están disponibles o están vacíos. "
                "Asegúrate de ejecutar `load_sesion` primero."
            )

    async def _drop_tables(self):
        """
        Elimina las columnas especificadas en `variables_to_change` del DataFrame `data_filtered_pilots`.
        """
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
        """
        Cambia las unidades de tiempo de milisegundos a minutos y segundos.
        """
        variables_to_change = [
            'Time', 'LapTime',
            'Sector1Time', 'Sector2Time', 'Sector3Time'
        ]

        if self.data_filtered_pilots is not None and not self.data_filtered_pilots.empty:
            for var in variables_to_change:
                if var in self.data_filtered_pilots.columns:
                    self.data_filtered_pilots[var] = self.data_filtered_pilots[var].apply(
                        lambda x: f"{int(x.total_seconds() // 60)
                                     }:{x.total_seconds() % 60:.3f}"
                        if pd.notnull(x) and isinstance(x, pd.Timedelta) else x
                    )
            print("Unidades de tiempo cambiadas a minutos y segundos para las variables:",
                  variables_to_change)
        else:
            print("Error: No hay datos filtrados disponibles para modificar. Asegúrate de ejecutar `filter_by_driver` primero.")

    async def data_to_json(self):
        """
        Convierte `data_filtered_pilots` a JSON y lo guarda en un archivo.
        """
        if self.data_filtered_pilots is not None and not self.data_filtered_pilots.empty:
            # Eliminar los índices llamando a la función _drop_tables
            await self._drop_tables()
            await self._change_units()

            # Convertir a JSON
            json_data = self.data_filtered_pilots.to_json(
                orient="records", indent=4, force_ascii=False)

            file_path = 'data/data_filtered_pilots.json'  # Guardar en el directorio actual
            # Guardar el archivo JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)

            print(f"Archivo JSON guardado en: {file_path}")
        else:
            print("Error: No hay datos filtrados disponibles para guardar. Asegúrate de ejecutar `filter_by_driver` primero.")


f1 = Session(
    2022,
    'belgium',
    'FP1',
    ['VER', "LEC", "RUS"]
)


async def main():
    await f1.load_sesion()
    print(f1)
    await f1.filter_by_driver()
    await f1.data_to_json()

# Run the main function
asyncio.run(main())
