-- Script per creare le tabelle in Supabase

-- Tabella ingredienti
CREATE TABLE IF NOT EXISTS ingredienti (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  nome VARCHAR(255) NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabella calendario
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

-- Indici per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_ingredienti_categoria ON ingredienti(categoria);
CREATE INDEX IF NOT EXISTS idx_calendario_giorno_pasto ON calendario(giorno, pasto);
