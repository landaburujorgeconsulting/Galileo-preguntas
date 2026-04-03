from flask import Flask, render_template, request, jsonify, send_file
import io
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

app = Flask(__name__)

# ===============================
# SECCIONES ESG
# ===============================

SECTIONS = [

# 1
{
"id": 1,
"title": "Gobernanza y Ética",
"questions": [
{"id":"q1","text":"¿Su organización cuenta con un Código de Ética aprobado?"},
{"id":"q2","text":"¿Dispone de política antisoborno y anticorrupción?"},
{"id":"q3","text":"¿Existe canal de denuncias confidencial?"},
{"id":"q4","text":"Casos confirmados de corrupción últimos 3 años"},
{"id":"q5","text":"¿Publica informe de sostenibilidad verificado?"}
]
},

# 2
{
"id": 2,
"title": "Derechos Humanos y Condiciones Laborales",
"questions": [
{"id":"q6","text":"¿Cuenta con política de derechos humanos UNGPs?"},
{"id":"q7","text":"¿Realiza debida diligencia en DDHH?"},
{"id":"q8","text":"¿Garantiza salario digno?"},
{"id":"q9","text":"¿Respeta libertad sindical?"},
{"id":"q10","text":"¿Previene trabajo infantil y forzoso?"},
{"id":"q11","text":"Tasa de rotación anual (%)"},
{"id":"q12","text":"Programas de capacitación empleados"},
{"id":"q13","text":"Política de no discriminación"}
]
},

# 3
{
"id":3,
"title":"Salud y Seguridad Ocupacional",
"questions":[
{"id":"q14","text":"Sistema SST certificado"},
{"id":"q15","text":"TRIR y LTIFR último año"},
{"id":"q16","text":"Simulacros y bienestar laboral"}
]
},

# 4
{
"id":4,
"title":"Cambio Climático y Energía",
"questions":[
{"id":"q17","text":"Inventario GEI Alcance 1-2-3"},
{"id":"q18","text":"Consumo energético y % renovables"},
{"id":"q19","text":"Metas SBTi"},
{"id":"q20","text":"Análisis riesgos climáticos"},
{"id":"q21","text":"Programa eficiencia energética"}
]
}

]  # ← CIERRE REAL DE SECTIONS


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

            elements.append(Paragraph(q["text"], styles["Heading4"]))
            elements.append(Paragraph(f"Respuesta: {answer}", styles["Normal"]))
            elements.append(Spacer(1, 12))

    doc.build(elements)

    buffer.seek(0)
    return buffer


# =============================
# HOME
# =============================

@app.route("/")
def index():
    return render_template("index.html", sections=SECTIONS)


# =============================
# SUBMIT
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
