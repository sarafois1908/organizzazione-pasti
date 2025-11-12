# Migrazione da SQLite a Supabase

Guida step-by-step per configurare Supabase nella tua app.

## 1. Crea un account Supabase

1. Vai su [supabase.com](https://supabase.com)
2. Fai login o crea un account
3. Crea un nuovo progetto

## 2. Recupera le credenziali

1. Nel dashboard di Supabase, vai a **Project Settings** → **API**
2. Copia:
   - **Project URL** → questo è il tuo `SUPABASE_URL`
   - **anon public** (chiave anonima) → questo è il tuo `SUPABASE_KEY`

## 3. Configura il database

### Opzione A: Usando SQL Editor di Supabase (consigliato)

1. Nel dashboard, vai a **SQL Editor**
2. Crea una nuova query
3. Copia e incolla il contenuto di `migration_supabase.sql`
4. Premi **Run** per eseguire

### Opzione B: Copia il comando SQL direttamente

Nel SQL Editor di Supabase, esegui:

```sql
CREATE TABLE IF NOT EXISTS ingredienti (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  nome VARCHAR(255) NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calendario (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  giorno VARCHAR(20) NOT NULL,
  pasto VARCHAR(10) NOT NULL,
  cereali TEXT,
  verdure TEXT,
  proteine TEXT,
  condimenti TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingredienti_categoria ON ingredienti(categoria);
CREATE INDEX IF NOT EXISTS idx_calendario_giorno_pasto ON calendario(giorno, pasto);
```

## 4. Configura le variabili d'ambiente

### Per sviluppo locale:

1. Copia `.env.example` in `.env`
2. Aggiungi le tue credenziali Supabase

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Per Streamlit Cloud:

1. Nel dashboard di Streamlit Cloud, vai alle impostazioni del repository
2. Aggiungi i secrets:

```
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

## 5. Installa le dipendenze

```bash
pip install -r requirements.txt
```

## 6. Testa la connessione

Esegui:

```bash
streamlit run PaginaIniziale.py
```

## 7. Migra i dati da SQLite (opzionale)

Se hai dati nel database SQLite locale, puoi migrarli a Supabase:

```python
import sqlite3
from db import supabase

# Connetti al database SQLite
conn = sqlite3.connect('piatti.db')
cursor = conn.cursor()

# Leggi ingredienti
cursor.execute('SELECT nome, categoria FROM ingredienti')
ingredienti_data = cursor.fetchall()

for nome, categoria in ingredienti_data:
    supabase.table('ingredienti').insert({
        'nome': nome,
        'categoria': categoria
    }).execute()

# Leggi calendario
cursor.execute('SELECT giorno, pasto, cereali, verdure, proteine, condimenti FROM calendario')
calendario_data = cursor.fetchall()

for row in calendario_data:
    supabase.table('calendario').insert({
        'giorno': row[0],
        'pasto': row[1],
        'cereali': row[2],
        'verdure': row[3],
        'proteine': row[4],
        'condimenti': row[5]
    }).execute()

conn.close()
print("✅ Migrazione completata!")
```

## Risoluzione problemi

### Errore: "Import supabase could not be resolved"

Esegui:
```bash
pip install supabase
```

### Errore: "SUPABASE_URL non configurato"

Assicurati di avere:
- File `.env` con le credenziali
- Oppure variabili d'ambiente impostate nel sistema

### Errore: "Unauthorized" da Supabase

Controlla che:
- La `SUPABASE_KEY` sia corretta (usa la chiave anonima, non quella segreta)
- Il progetto Supabase sia attivo
- Le tabelle siano create correttamente

## Prossimi passi

- ✅ Backup regolare su Supabase
- ✅ Aggiorna la tua app Streamlit nella cloud
- ✅ Considera di abilitare l'autenticazione Supabase per gestire gli utenti
