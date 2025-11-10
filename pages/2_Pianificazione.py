import streamlit as st
from db import session, ingredienti, calendario
import pandas as pd

st.title("📅 Inserimento Pianificazione")

giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
pasti = ["Pranzo","Cena"]

ingredienti_db = session.execute(ingredienti.select()).fetchall()
cereali_opts = [i.nome for i in ingredienti_db if i.categoria == "cereali"]
verdure_opts = [i.nome for i in ingredienti_db if i.categoria == "verdure"]
proteine_opts = [i.nome for i in ingredienti_db if i.categoria == "proteine"]
condimenti_opts = [i.nome for i in ingredienti_db if i.categoria == "condimenti"]

existing = session.execute(calendario.select()).mappings().all()
existing_df = pd.DataFrame(existing) if existing else pd.DataFrame(columns=["giorno","pasto","cereali","verdure","proteine","condimenti"])

def get_existing_list(g, p, col):
    if existing_df.empty:
        return []
    row = existing_df[(existing_df["giorno"] == g) & (existing_df["pasto"] == p)]
    if row.empty:
        return []
    val = str(row.iloc[0].get(col, "") or "")
    return [x.strip() for x in val.split(",") if x.strip()]

pasti_selezionati = []
for g in giorni:
    with st.expander(f"📅 {g}", expanded=False):
        col_pranzo, col_cena = st.columns(2)
        with col_pranzo:
            st.write("**Pranzo**")
            cereali_p = st.multiselect("Cereali", options=cereali_opts, default=get_existing_list(g, "Pranzo", "cereali"), key=f"{g}_pranzo_cereali")
            verdure_p = st.multiselect("Verdure", options=verdure_opts, default=get_existing_list(g, "Pranzo", "verdure"), key=f"{g}_pranzo_verdure")
            proteine_p = st.multiselect("Proteine", options=proteine_opts, default=get_existing_list(g, "Pranzo", "proteine"), key=f"{g}_pranzo_proteine")
            condimenti_p = st.multiselect("Condimenti", options=condimenti_opts, default=get_existing_list(g, "Pranzo", "condimenti"), key=f"{g}_pranzo_condimenti")
        with col_cena:
            st.write("**Cena**")
            cereali_c = st.multiselect("Cereali", options=cereali_opts, default=get_existing_list(g, "Cena", "cereali"), key=f"{g}_cena_cereali")
            verdure_c = st.multiselect("Verdure", options=verdure_opts, default=get_existing_list(g, "Cena", "verdure"), key=f"{g}_cena_verdure")
            proteine_c = st.multiselect("Proteine", options=proteine_opts, default=get_existing_list(g, "Cena", "proteine"), key=f"{g}_cena_proteine")
            condimenti_c = st.multiselect("Condimenti", options=condimenti_opts, default=get_existing_list(g, "Cena", "condimenti"), key=f"{g}_cena_condimenti")
        pasti_selezionati.append({"giorno": g, "pasto": "Pranzo", "cereali": ", ".join(cereali_p), "verdure": ", ".join(verdure_p), "proteine": ", ".join(proteine_p), "condimenti": ", ".join(condimenti_p)})
        pasti_selezionati.append({"giorno": g, "pasto": "Cena", "cereali": ", ".join(cereali_c), "verdure": ", ".join(verdure_c), "proteine": ", ".join(proteine_c), "condimenti": ", ".join(condimenti_c)})

if st.button("💾 Salva calendario"):
    session.execute(calendario.delete())
    for row in pasti_selezionati:
        session.execute(calendario.insert().values(**row))
    session.commit()
    st.success("Calendario salvato!")
    st.rerun()