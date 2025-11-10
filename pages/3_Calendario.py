import streamlit as st
import pandas as pd
from db import session, calendario
from datetime import datetime, timedelta

st.set_page_config(page_title="Promemoria Ammollo", layout="wide")
st.title("⏰ Pasti salvati & Ammollo Legumi")

giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
pasti = ["Pranzo", "Cena"]

calendario_db = session.execute(calendario.select()).mappings().all()

if calendario_db:
    df_saved = pd.DataFrame(calendario_db).drop(columns=["id"])
    df_saved["giorno"] = pd.Categorical(df_saved["giorno"], categories=giorni, ordered=True)
    df_saved["pasto"] = pd.Categorical(df_saved["pasto"], categories=pasti, ordered=True)
    df_saved = df_saved.sort_values(["giorno", "pasto"])

    st.subheader("📖 Calendario settimanale (visualizzazione grafica)")
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

    def promemoria_ammollo(df):
        legumi = ["Ceci", "Fagioli Cannellini", "Fagioli Borlotti"]
        avvisi = []
        idx = {g: i for i, g in enumerate(giorni)}

        for _, row in df.iterrows():
            giorno = row["giorno"]
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
        idx = {g:i for i,g in enumerate(giorni)}

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
        st.subheader("📋 Tabella promemoria ammollo")
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