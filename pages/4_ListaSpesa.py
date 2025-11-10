import streamlit as st
import pandas as pd
from db import session, calendario
from collections import Counter

st.set_page_config(page_title="Lista della Spesa", layout="wide")
st.title("🛒 Lista della Spesa")

calendario_db = session.execute(calendario.select()).mappings().all()

if calendario_db:
    cat_keys = ["cereali", "verdure", "proteine", "condimenti"]
    grouped_items = {cat: [] for cat in cat_keys}

    for row in calendario_db:
        for cat in cat_keys:
            if row.get(cat):
                items = [x.strip() for x in str(row.get(cat, "")).split(",") if x.strip()]
                grouped_items[cat].extend(items)

    for cat in cat_keys:
        counter = Counter(grouped_items[cat])
        st.write(f"### {cat.capitalize()}")
        if counter:
            for item, count in sorted(counter.items(), key=lambda x: x[0].lower()):
                st.write(f"- {item} x{count}")
        else:
            st.info(f"Nessun {cat} selezionato.")
else:
    st.info("La lista della spesa sarà disponibile dopo aver salvato almeno un pasto.")