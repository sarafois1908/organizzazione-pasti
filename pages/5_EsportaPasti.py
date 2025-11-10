import streamlit as st
from db import session, calendario
from datetime import datetime, timedelta
from fpdf import FPDF
import io
import os

# Configura la pagina
st.set_page_config(page_title="Esporta pasti (.ics + .pdf)", layout="wide")
st.title("📦 Esporta pasti settimanali (.ics + .pdf)")

# Giorni e pasti
giorni = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
pasti = ["Pranzo", "Cena"]
idx = {g:i for i,g in enumerate(giorni)}

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

        titolo = f"{giorno} - {pasto} 🍽️ {cereali}, {proteine}, {verdure}"
        descrizione = f"""🍚 Cereali: {cereali}
🥦 Verdure: {verdure}
🫘 Proteine: {proteine}
🧂 Condimenti: {condimenti}"""

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

# Funzione per creare PDF con emoji usando fpdf2
def crea_pdf(calendario_db):
    pdf = FPDF()
    font_path = "DejaVuSans.ttf"

    if not os.path.exists(font_path):
        st.error("⚠️ Il file DejaVuSans.ttf non è presente nella cartella del progetto.")
        return None

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 16)
    pdf.cell(0, 10, "📅 Pasti settimanali", ln=True)

    for giorno in giorni:
        pdf.set_font("DejaVu", "", 14)
        pdf.cell(0, 10, f"\n{giorno}", ln=True)

        for pasto in pasti:
            pasti_giorno = [r for r in calendario_db if r["giorno"] == giorno and r["pasto"] == pasto]
            if len(pasti_giorno) > 0:
                row = pasti_giorno[0]
                pdf.set_font("DejaVu", "", 12)
                pdf.cell(0, 10, f"{pasto} 🍽️", ln=True)
                pdf.multi_cell(0, 8, f"""🍚 Cereali: {row['cereali']}
🥦 Verdure: {row['verdure']}
🫘 Proteine: {row['proteine']}
🧂 Condimenti: {row['condimenti']}""")

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# Se ci sono pasti salvati
if calendario_db:
    # Bottone ICS
    ics_file = crea_eventi_ics(calendario_db)
    st.download_button(
        label="📥 Scarica pasti settimanali (.ics)",
        data=ics_file,
        file_name="pasti_settimanali.ics",
        mime="text/calendar"
    )

    # Bottone PDF
    pdf_file = crea_pdf(calendario_db)
    if pdf_file:
        st.download_button(
            label="📄 Scarica pasti settimanali (.pdf)",
            data=pdf_file,
            file_name="pasti_settimanali.pdf",
            mime="application/pdf"
        )
else:
    st.info("Nessun pasto salvato nel calendario.")
