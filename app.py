from flask import Flask, render_template, request, jsonify, send_file
import io
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

app = Flask(__name__)

# =============================
# EJEMPLO MINIMO DE SECTIONS
# (dejá el tuyo completo)
# =============================

SECTIONS = [
    {
        "id": 1,
        "title": "Gobernanza",
        "questions": [
            {"id": "q1", "text": "Tiene codigo de etica?"}
        ]
    }
]

# =============================
# GENERAR PDF
# =============================

def generate_pdf(form_data, company_name, contact_name, contact_email):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("DIAGNOSTICO DE SOSTENIBILIDAD", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Empresa: {company_name}", styles["Normal"]))
    elements.append(Paragraph(f"Contacto: {contact_name}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {contact_email}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    for section in SECTIONS:

        elements.append(
            Paragraph(
                f"{section['id']}. {section['title']}",
                styles["Heading2"]
            )
        )

        for q in section["questions"]:
            answer = form_data.get(q["id"], "Sin respuesta")

            elements.append(
                Paragraph(q["text"], styles["Heading4"])
            )

            elements.append(
                Paragraph(f"Respuesta: {answer}", styles["Normal"])
            )

        elements.append(Spacer(1, 12))

    # 🔥 CREA EL PDF
    doc.build(elements)

    # 🔥 FUNDAMENTAL
    buffer.seek(0)

    return buffer


# =============================
# HOME
# =============================

@app.route("/")
def index():
    return render_template("index.html", sections=SECTIONS)


# =============================
# GENERAR PDF DESDE FRONTEND
# =============================

@app.route("/submit", methods=["POST"])
def submit():

    try:
        data = request.json

        company_name = data.get("company_name", "")
        contact_name = data.get("contact_name", "")
        contact_email = data.get("contact_email", "")
        answers = data.get("answers", {})

        pdf_buffer = generate_pdf(
            answers,
            company_name,
            contact_name,
            contact_email
        )

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="diagnostico_sostenibilidad.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("ERROR REAL:", e)
        return jsonify({"error": str(e)}), 500


# =============================
# RUN
# =============================

if __name__ == "__main__":
    app.run(debug=True)
