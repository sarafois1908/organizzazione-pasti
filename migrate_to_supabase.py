"""
Script per migrare dati da SQLite a Supabase
Esegui: python migrate_to_supabase.py
"""

import os
import sqlite3
import sys
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Errore: configura SUPABASE_URL e SUPABASE_KEY nel file .env")
    sys.exit(1)

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Errore di connessione a Supabase: {e}")
    sys.exit(1)

def migrate_ingredienti():
    """Migra gli ingredienti da SQLite a Supabase"""
    print("\n📦 Migrando ingredienti...")
    
    try:
        conn = sqlite3.connect('piatti.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT nome, categoria FROM ingredienti')
        ingredienti_data = cursor.fetchall()
        
        if not ingredienti_data:
            print("⚠️  Nessun ingrediente trovato nel database SQLite")
            return
        
        for row in ingredienti_data:
            data = {
                'nome': row['nome'],
                'categoria': row['categoria']
            }
            supabase.table('ingredienti').insert(data).execute()
        
        print(f"✅ {len(ingredienti_data)} ingredienti migrati con successo!")
        conn.close()
        
    except FileNotFoundError:
        print("⚠️  File piatti.db non trovato. Saltando ingredienti.")
    except Exception as e:
        print(f"❌ Errore durante la migrazione ingredienti: {e}")

def migrate_calendario():
    """Migra il calendario da SQLite a Supabase"""
    print("\n📅 Migrando calendario...")
    
    try:
        conn = sqlite3.connect('piatti.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT giorno, pasto, cereali, verdure, proteine, condimenti FROM calendario')
        calendario_data = cursor.fetchall()
        
        if not calendario_data:
            print("⚠️  Nessun pasto trovato nel database SQLite")
            return
        
        for row in calendario_data:
            data = {
                'giorno': row['giorno'],
                'pasto': row['pasto'],
                'cereali': row['cereali'],
                'verdure': row['verdure'],
                'proteine': row['proteine'],
                'condimenti': row['condimenti']
            }
            supabase.table('calendario').insert(data).execute()
        
        print(f"✅ {len(calendario_data)} pasti migrati con successo!")
        conn.close()
        
    except FileNotFoundError:
        print("⚠️  File piatti.db non trovato. Saltando calendario.")
    except Exception as e:
        print(f"❌ Errore durante la migrazione calendario: {e}")

def main():
    print("=" * 60)
    print("🚀 Inizio migrazione da SQLite a Supabase")
    print("=" * 60)
    
    migrate_ingredienti()
    migrate_calendario()
    
    print("\n" + "=" * 60)
    print("✅ Migrazione completata!")
    print("=" * 60)
    print("\nPuoi ora eliminare il file piatti.db se desideri.")

if __name__ == "__main__":
    main()
