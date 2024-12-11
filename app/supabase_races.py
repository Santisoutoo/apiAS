import os
from supabase import create_client, Client
from dotenv import load_dotenv


class SupabaseDataCircuit():
    def __init__(self, tabla, select = '*' circuit = None):

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
        self.circuit = circuit

    def fetch_data(self):
        return self.supabase.table(self.tabla).select(self.select).execute()
    
    def fetch_data_by_circuit(self, tabla, circuit):
        pass
    

    def update_number_races(self):
        pass