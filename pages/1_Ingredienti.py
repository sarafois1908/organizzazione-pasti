import streamlit as st
from db import session, ingredienti
import pandas as pd

st.title("🧅 Gestione Ingredienti")

st.subheader("Inserisci liste di ingredienti (uno per riga)")
col_a, col_b = st.columns(2)
with col_a:
    input_cereali = st.text_area("Cereali")
    input_proteine = st.text_area("Proteine")
with col_b:
    input_verdure = st.text_area("Verdure")
    input_condimenti = st.text_area("Condimenti")

if st.button("💾 Salva liste"):
    def salva_lista(testo, categoria):
        rows = [r.strip() for r in testo.split("\n") if r.strip()]
        for nome in rows:
            session.execute(ingredienti.insert().values(nome=nome, categoria=categoria))
    salva_lista(input_cereali, "cereali")
    salva_lista(input_verdure, "verdure")
    salva_lista(input_proteine, "proteine")
    salva_lista(input_condimenti, "condimenti")
    session.commit()
    st.success("Liste salvate nel database!")
    st.rerun()

st.subheader("Ingredienti disponibili")
compact_all = st.checkbox("Compatta tutte le liste", value=True)
ingredienti_db = session.execute(ingredienti.select()).fetchall()
categorie = ["cereali", "verdure", "proteine", "condimenti"]

for cat in categorie:
    lista = [i for i in ingredienti_db if i.categoria == cat]
    count = len(lista)
    with st.expander(f"{cat.capitalize()} ({count})", expanded=not compact_all):
        if count == 0:
            st.info(f"Nessun elemento per {cat}.")
        else:
            if st.button(f"❌ Elimina tutti {cat}", key=f"del_all_{cat}"):
                session.execute(ingredienti.delete().where(ingredienti.c.categoria == cat))
                session.commit()
                st.success(f"Lista {cat} eliminata.")
                st.rerun()
            for i in lista:
                c1, c2 = st.columns([4,1])
                c1.write(f"- {i.nome}")
                if c2.button("❌ Elimina", key=f"del_{i.id}"):
                    session.execute(ingredienti.delete().where(ingredienti.c.id == i.id))
                    session.commit()
                    st.rerun()