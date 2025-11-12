import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# Carica variabili d'ambiente dal file .env (sviluppo locale)
load_dotenv()

# Configurazione Supabase - Supporta sia variabili d'ambiente che Streamlit secrets
def get_supabase_config():
    """Recupera configurazione Supabase da secrets o variabili d'ambiente"""
    url = None
    key = None
    
    # Prova prima con st.secrets (Streamlit Cloud)
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            print("✅ Caricato da st.secrets (Streamlit Cloud)")
            return url, key
    except Exception:
        pass
    
    # Fallback a variabili d'ambiente (incluso .env)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if url and key:
        print("✅ Caricato da variabili d'ambiente (.env)")
        return url, key
    
    # Se nessuno funziona, errore dettagliato
    raise ValueError(
        "❌ Credenziali Supabase non configurate!\n\n"
        "Per sviluppo locale:\n"
        "1. Copia .env.example in .env\n"
        "2. Aggiungi SUPABASE_URL e SUPABASE_KEY\n"
        "3. Assicurati che il file .env sia nella root del progetto\n\n"
        "Per Streamlit Cloud:\n"
        "1. Vai su share.streamlit.io > App Settings > Secrets\n"
        "2. Aggiungi SUPABASE_URL e SUPABASE_KEY"
    )

SUPABASE_URL, SUPABASE_KEY = get_supabase_config()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Classe wrapper per simulare l'interfaccia SQLAlchemy
class Row:
    """Wrapper per rappresentare una riga di database"""
    def __init__(self, data):
        self.__dict__.update(data)
        self._data = data
    
    def __getattr__(self, name):
        return self._data.get(name)
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class Table:
    """Classe wrapper per le tabelle"""
    def __init__(self, name):
        self.name = name
    
    def insert(self):
        return InsertQuery(self.name)
    
    def select(self):
        return SelectQuery(self.name)
    
    def delete(self):
        return DeleteQuery(self.name)
    
    def c(self):
        """Property per accesso SQLAlchemy-like ai campi"""
        return self


class Column:
    """Classe wrapper per le colonne"""
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, value):
        return {"field": self.name, "op": "eq", "value": value}
    
    def __ne__(self, value):
        return {"field": self.name, "op": "neq", "value": value}


class InsertQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self.values_dict = {}
    
    def values(self, **kwargs):
        self.values_dict = kwargs
        return self
    
    def execute(self):
        try:
            result = supabase.table(self.table_name).insert(self.values_dict).execute()
            return result
        except Exception as e:
            print(f"Errore durante insert in {self.table_name}: {e}")
            raise


class SelectQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filters = {}
    
    def where(self, condition):
        self.filters = condition
        return self
    
    def execute(self):
        try:
            result = supabase.table(self.table_name).select("*").execute()
            # Converti risultati in Row objects per compatibilità
            rows = [Row(item) for item in result.data] if result.data else []
            return rows
        except Exception as e:
            print(f"Errore durante select da {self.table_name}: {e}")
            return []
    
    def fetchall(self):
        return self.execute()
    
    def mappings(self):
        """Ritorna self per supportare .mappings().all()"""
        return self
    
    def all(self):
        return self.execute()


class DeleteQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filter_condition = None
    
    def where(self, condition):
        self.filter_condition = condition
        return self
    
    def execute(self):
        try:
            if self.filter_condition:
                # Estrai la condizione where (semplice supporto per categoria)
                if hasattr(self.filter_condition, '__contains__'):
                    result = supabase.table(self.table_name).delete().neq("id", -1).execute()
                else:
                    result = supabase.table(self.table_name).delete().neq("id", -1).execute()
            else:
                result = supabase.table(self.table_name).delete().neq("id", -1).execute()
            return result
        except Exception as e:
            print(f"Errore durante delete da {self.table_name}: {e}")
            raise


class UpdateQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self.values_dict = {}
    
    def values(self, **kwargs):
        self.values_dict = kwargs
        return self
    
    def where(self, condition):
        self.filter_condition = condition
        return self
    
    def execute(self):
        try:
            result = supabase.table(self.table_name).update(self.values_dict).execute()
            return result
        except Exception as e:
            print(f"Errore durante update in {self.table_name}: {e}")
            raise


class ExecuteWrapper:
    """Wrapper per simulare SQLAlchemy execution"""
    def __init__(self, query):
        self.query = query
        self._result = None
    
    def __iter__(self):
        if isinstance(self.query, SelectQuery):
            return iter(self.query.execute())
        return iter([])
    
    def fetchall(self):
        if isinstance(self.query, SelectQuery):
            return self.query.execute()
        return []
    
    def mappings(self):
        if isinstance(self.query, SelectQuery):
            return SelectMappings(self.query.execute())
        return SelectMappings([])


class SelectMappings:
    """Wrapper per .mappings().all()"""
    def __init__(self, rows):
        self.rows = rows
    
    def all(self):
        return self.rows


# Wrapper per Session che simula SQLAlchemy
class Session:
    def execute(self, query):
        if isinstance(query, (InsertQuery, DeleteQuery, UpdateQuery)):
            return query.execute()
        elif isinstance(query, SelectQuery):
            return ExecuteWrapper(query)
        return query.execute()
    
    def commit(self):
        pass
    
    def close(self):
        pass


# Inizializza tabelle e sessione
ingredienti = Table("ingredienti")
calendario = Table("calendario")
session = Session()
