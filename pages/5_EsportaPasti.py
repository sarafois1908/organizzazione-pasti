import streamlit as st
from db import session, calendario
from datetime import datetime, timedelta

st.set_page_config(page_title="Esporta pasti (.ics)", layout="wide")
st.title("📅 Esporta pasti settimanali (.ics) con ingredienti e orari")

giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
pasti = ["Pranzo", "Cena"]
idx = {g:i for i,g in enumerate(giorni)}

calendario_db = session.execute(calendario.select()).mappings().all()

def crea_eventi_ics(calendario_db):
    eventi = []
    oggi = datetime.today()

    for row in calendario_db:
        giorno = row["giorno"]
        pasto = row["pasto"]

        # Ingredienti per categoria
        cereali = row.get("cereali", "")
        verdure = row.get("verdure", "")
        proteine = row.get("proteine", "")
        condimenti = row.get("condimenti", "")

        # Titolo con ingredienti principali
        titolo = f"{giorno} - {pasto} 🍽️ {cereali}, {proteine}, {verdure}"

        # Descrizione dettagliata
        descrizione = f"""🍚 Cereali: {cereali}
🥦 Verdure: {verdure}
🫘 Proteine: {proteine}
🧂 Condimenti: {condimenti}"""

        # Calcolo data e orario evento
        delta = (idx[giorno] - oggi.weekday()) % 7
        data_evento = oggi + timedelta(days=delta)

        if pasto == "Pranzo":
            ora_evento = "130000"
        else:
            ora_evento = "200000"

        dtstart = data_evento.strftime("%Y%m%d") + "T" + ora_evento
        dtend = data_evento.strftime("%Y%m%d") + "T" + str(int(ora_evento[:2]) + 1).zfill(2) + "0000"

        eventi.append(f"""BEGIN:VEVENT
SUMMARY:{titolo}
DESCRIPTION:{descrizione}
DTSTART:{dtstart}
DTEND:{dtend}
END:VEVENT""")

    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\n" + "\n".join(eventi) + "\nEND:VCALENDAR"
    return ics_content

if calendario_db:
    ics_file = crea_eventi_ics(calendario_db)
    st.download_button(
        label="📥 Scarica pasti settimanali con ingredienti (.ics)",
        data=ics_file,
        file_name="pasti_settimanali.ics",
        mime="text/calendar"
    )
else:
    st.info("Nessun pasto salvato nel calendario.")
