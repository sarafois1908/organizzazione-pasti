import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

# --- Configurazione DB ---
DB_PATH = "piatti.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
metadata = MetaData()

ingredienti = Table(
    "ingredienti", metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String),
    Column("categoria", String)  # cereali, verdure, proteine, condimenti
)

calendario = Table(
    "calendario", metadata,
    Column("id", Integer, primary_key=True),
    Column("giorno", String),      # Lunedì ... Domenica
    Column("pasto", String),       # Pranzo o Cena
    Column("cereali", String),
    Column("verdure", String),
    Column("proteine", String),
    Column("condimenti", String)
)

metadata.create_all(engine)
Session = sessionmaker(bind=engine, future=True)
session = Session()

st.title("🍽️ Gestione ingredienti + Calendario settimanale + Lista della spesa")

# --- Sezione: Inserimento liste di ingredienti ---
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
# --- Sezione: Calendario settimanale COMPATTO ---
st.subheader("📅 Calendario settimanale (Pranzo e Cena)")
ingredienti_db = session.execute(ingredienti.select()).fetchall()
cereali_opts = [i.nome for i in ingredienti_db if i.categoria == "cereali"]
verdure_opts = [i.nome for i in ingredienti_db if i.categoria == "verdure"]
proteine_opts = [i.nome for i in ingredienti_db if i.categoria == "proteine"]
condimenti_opts = [i.nome for i in ingredienti_db if i.categoria == "condimenti"]

giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
pasti = ["Pranzo","Cena"]

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
# --- Visualizzazione riassuntiva grafica (collassabile) ---
st.subheader("📖 Calendario riassuntivo grafico")
calendario_db = session.execute(calendario.select()).mappings().all()

if calendario_db:
    df_saved = pd.DataFrame(calendario_db).drop(columns=["id"])
    df_saved["giorno"] = pd.Categorical(df_saved["giorno"], categories=giorni, ordered=True)
    df_saved["pasto"] = pd.Categorical(df_saved["pasto"], categories=pasti, ordered=True)
    df_saved = df_saved.sort_values(["giorno", "pasto"])

    for g in giorni:
        df_day = df_saved[df_saved["giorno"] == g]
        if not df_day.empty:
            with st.expander(f"📅 {g}", expanded=False):
                for _, row in df_day.iterrows():
                    pasto = row["pasto"]
                    st.markdown(
                        f"""
                        <div style="padding:10px; margin:5px; border-radius:8px; background-color:#f0f8ff; color:#000000;">
                            <b>{pasto}</b><br>
                            🍚 Cereali: {row['cereali']}<br>
                            🥦 Verdure: {row['verdure']}<br>
                            🍗 Proteine: {row['proteine']}<br>
                            🧂 Condimenti: {row['condimenti']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


    # --- Promemoria ammollo legumi in tabella con quantità ---
    def promemoria_ammollo(df):
        legumi = ["Ceci", "Fagioli Cannellini", "Fagioli Borlotti"]
        avvisi = []
        idx = {g: i for i, g in enumerate(giorni)}

        for _, row in df.iterrows():
            giorno = row["giorno"]
            pasto = row["pasto"]
            for cat in ["cereali", "verdure", "proteine", "condimenti"]:
                ingredienti = [x.strip() for x in str(row[cat]).split(",") if x.strip()]
                for legume in legumi:
                    if legume in ingredienti:
                        prev_idx = (idx[giorno] - 1) % 7
                        giorno_precedente = giorni[prev_idx]
                        avvisi.append({"Giorno": giorno_precedente, "Legume": legume})

        if avvisi:
            df_avvisi = pd.DataFrame(avvisi)
            df_avvisi = df_avvisi.groupby(["Giorno", "Legume"]).size().reset_index(name="Quantità")
            return df_avvisi
        else:
            return pd.DataFrame(columns=["Giorno", "Legume", "Quantità"])

    def crea_file_ics(df_avvisi):
        eventi = []
        giorni_map = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
        idx = {g:i for i,g in enumerate(giorni_map)}

        for _, row in df_avvisi.iterrows():
            giorno = row["Giorno"]
            legume = row["Legume"]
            qty = row["Quantità"]

            oggi = datetime.today()
            target_idx = idx[giorno]
            delta = (target_idx - oggi.weekday()) % 7
            data_evento = oggi + timedelta(days=delta)

            titolo = f"Mettere in ammollo {legume} (x{qty})"
            eventi.append(f"""BEGIN:VEVENT
SUMMARY:{titolo}
DTSTART;VALUE=DATE:{data_evento.strftime("%Y%m%d")}
DTEND;VALUE=DATE:{(data_evento + timedelta(days=1)).strftime("%Y%m%d")}
END:VEVENT""")

        ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\n" + "\n".join(eventi) + "\nEND:VCALENDAR"
        return ics_content

    df_avvisi = promemoria_ammollo(df_saved)
    if not df_avvisi.empty:
        st.subheader("⏰ Tabella promemoria ammollo legumi")
        st.table(df_avvisi)

        ics_file = crea_file_ics(df_avvisi)
        st.download_button(
            label="📥 Scarica promemoria ammollo (.ics)",
            data=ics_file,
            file_name="promemoria_ammollo.ics",
            mime="text/calendar"
        )
else:
    st.info("Nessun pasto salvato ancora.")

# --- Lista della spesa raggruppata per categoria ---
st.subheader("🛒 Lista della spesa (raggruppata per categoria)")

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