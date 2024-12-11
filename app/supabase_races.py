import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict

class SupabaseDataCircuit():
    def __init__(self, tabla, select = '*', circuito = None):

        #Varibales entorno
        load_dotenv()

        # URL Supabase datos circuito
        SUPABASE_URL = os.getenv("SUPABASE_URL_DATOS")

        # API KEY datos circuito
        SUPABASE_KEY = os.getenv("SUPABASE_KEY_DATOS")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Debe de proporcionarse una dirección" 
                "y clave de API para conectarse"
            )
        self.supabase: Client = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        self.tabla = tabla
        self.select = select
        self.circuito = circuito

    def fetch_data(self):
        return self.supabase.table(self.tabla).select(self.select).execute()

    def fetch_data_by_circuit(self, circuit: str):
        """
        Obtiene datos específicos de un circuito.
        """
        response = self.supabase.table(self.tabla).\
            select(self.select). \
            eq("circuito", circuit). \
            execute()
        return response
    
    def delete_race(self, race_name: str):
        """
        Elimina una carrera de la tabla `datos_circuitos` de Supabase en base al nombre.
        Args:
            race_name (str): Nombre de la carrera a eliminar.
        """
        response = (
            self.supabase.table(self.tabla)
            .delete()
            .eq("circuito", race_name)
            .execute()
        )
        return response.data
    
    def update_circuit_information(self, circuit_id: int, update_data: Dict):
        """
        Actualiza la información de un circuito en la tabla `datos_circuitos` de Supabase.
        Args:
            circuit_id (int): ID del circuito a actualizar.
            update_data (Dict): Diccionario con los campos a actualizar.
        """
        response = (
            self.supabase.table(self.tabla)
            .update(update_data)
            .eq("id", circuit_id)
            .execute()
        )
        return response
    
    def create_race(self, race_data: Dict):
        """
        Inserta una nueva carrera en la tabla `datos_circuitos` de Supabase.
        Args:
            race_data (Dict): Diccionario con los datos de la carrera a insertar.
        """
        response = self.supabase.table(self.tabla).insert(race_data).execute()
        return response







