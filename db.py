from supabase import create_client

SUPABASE_URL = "https://kcnrqzcosclwmdngeksr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjbnJxemNvc2Nsd21kbmdla3NyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5MzU4NDYsImV4cCI6MjA3ODUxMTg0Nn0.gRl3IMwSPvz1kwqzDeRZWeDFQYbdE9fWW9oKW5a7S8Y"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
