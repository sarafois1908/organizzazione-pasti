import streamlit as st
from db import session, calendario
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# Configura la pagina
st.set_page_config(page_title="Esporta pasti (.ics + .pdf)", layout="wide")
st.title("Esporta pasti settimanali (.ics + .pdf)")

# Giorni e pasti
giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
pasti = ["Pranzo", "Cena"]
idx = {g: i for i, g in enumerate(giorni)}

# Recupera dati dal database
calendario_db = session.execute(calendario.select()).mappings().all()

# Funzione per creare file ICS
def crea_eventi_ics(calendario_db):
    eventi = []
    oggi = datetime.today()

    for row in calendario_db:
        giorno = row["giorno"]
        pasto = row["pasto"]

        cereali = row.get("cereali", "")
        verdure = row.get("verdure", "")
        proteine = row.get("proteine", "")
        condimenti = row.get("condimenti", "")

        titolo = f"{giorno} - {pasto}: {cereali}, {proteine}, {verdure}"
        descrizione = f"""Cereali: {cereali}
Verdure: {verdure}
Proteine: {proteine}
Condimenti: {condimenti}"""

        delta = (idx[giorno] - oggi.weekday()) % 7
        data_evento = oggi + timedelta(days=delta)
        ora_evento = "130000" if pasto == "Pranzo" else "200000"
        dtstart = data_evento.strftime("%Y%m%d") + "T" + ora_evento
        dtend = data_evento.strftime("%Y%m%d") + "T" + str(int(ora_evento[:2]) + 1).zfill(2) + "0000"

        eventi.append(f"""BEGIN:VEVENT
SUMMARY:{titolo}
DESCRIPTION:{descrizione}
DTSTART:{dtstart}
DTEND:{dtend}
END:VEVENT""")

    return "BEGIN:VCALENDAR\nVERSION:2.0\n" + "\n".join(eventi) + "\nEND:VCALENDAR"

# Funzione per creare PDF con layout ordinato
def crea_pdf(calendario_db):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titolo principale
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "Pasti settimanali", ln=True)
    pdf.ln(5)

    for giorno in giorni:
        # Intestazione del giorno
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 0, 128)  # blu scuro
        pdf.cell(0, 10, giorno, ln=True)
        pdf.set_text_color(0, 0, 0)  # reset colore

        for pasto in pasti:
            pasto_data = next(
                (r for r in calendario_db if r["giorno"] == giorno and r["pasto"] == pasto),
                None
            )

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"{pasto}:", ln=True)

            pdf.set_font("Arial", "", 11)
            if pasto_data:
                pdf.multi_cell(0, 7, f"""Cereali: {pasto_data['cereali']}
Verdure: {pasto_data['verdure']}
Proteine: {pasto_data['proteine']}
Condimenti: {pasto_data['condimenti']}""")
            else:
                pdf.cell(0, 7, "Nessun pasto salvato", ln=True)

            pdf.ln(3)  # spazio tra pranzo e cena

        pdf.ln(5)  # spazio tra giorni

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

# Se ci sono pasti salvati
if calendario_db:
    # Bottone ICS
    ics_file = crea_eventi_ics(calendario_db)
    st.download_button(
        label="📅Scarica pasti settimanali (.ics)",
        data=ics_file,
        file_name="pasti_settimanali.ics",
        mime="text/calendar"
    )

    # Bottone PDF
    pdf_file = crea_pdf(calendario_db)
    if pdf_file:
        st.download_button(
            label="📄Scarica pasti settimanali (.pdf)",
            data=pdf_file,
            file_name="pasti_settimanali.pdf",
            mime="application/pdf"
        )
else:
    st.info("Nessun pasto salvato nel calendario.")
