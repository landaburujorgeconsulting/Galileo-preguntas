from flask import Flask, render_template, request, send_file, jsonify
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

app = Flask(__name__)

# =========================
# SECCIONES ESG (14 / 60)
# =========================

SECTIONS = [

{
"id":1,
"title":"Gobernanza y Ética",
"questions":[
{"id":"q1","text":"Código de ética"},
{"id":"q2","text":"Política antisoborno"},
{"id":"q3","text":"Canal denuncias"},
{"id":"q4","text":"Casos corrupción"},
{"id":"q5","text":"Reporte sostenibilidad"}
]
},

{
"id":2,
"title":"Derechos Humanos",
"questions":[
{"id":"q6","text":"Política DDHH"},
{"id":"q7","text":"Debida diligencia"},
{"id":"q8","text":"Salario digno"},
{"id":"q9","text":"Libertad sindical"},
{"id":"q10","text":"Trabajo infantil"},
{"id":"q11","text":"Rotación anual"},
{"id":"q12","text":"Capacitación"},
{"id":"q13","text":"No discriminación"}
]
},

{
"id":3,
"title":"Salud y Seguridad",
"questions":[
{"id":"q14","text":"Sistema SST"},
{"id":"q15","text":"Indicadores accidentes"},
{"id":"q16","text":"Bienestar laboral"}
]
},

{
"id":4,
"title":"Cambio Climático",
"questions":[
{"id":"q17","text":"Inventario GEI"},
{"id":"q18","text":"Consumo energía"},
{"id":"q19","text":"Metas climáticas"},
{"id":"q20","text":"Riesgos climáticos"},
{"id":"q21","text":"Eficiencia energética"}
]
},

{
"id":5,
"title":"Agua y Biodiversidad",
"questions":[
{"id":"q22","text":"Consumo agua"},
{"id":"q23","text":"Estrés hídrico"},
{"id":"q24","text":"Política biodiversidad"}
]
},

{
"id":6,
"title":"Residuos",
"questions":[
{"id":"q25","text":"Residuos generados"},
{"id":"q26","text":"Economía circular"},
{"id":"q27","text":"Reducción plásticos"}
]
},

{
"id":7,
"title":"Cadena Suministro",
"questions":[
{"id":"q28","text":"Compras sostenibles"},
{"id":"q29","text":"Evaluación proveedores"},
{"id":"q30","text":"Compras locales"},
{"id":"q31","text":"Auditorías"},
{"id":"q32","text":"Código proveedores"},
{"id":"q33","text":"Programa PYME"},
{"id":"q34","text":"Cláusulas ESG"}
]
},

{
"id":8,
"title":"Minerales",
"questions":[
{"id":"q35","text":"Minerales conflicto"},
{"id":"q36","text":"Trazabilidad"},
{"id":"q37","text":"Material reciclado"}
]
},

{
"id":9,
"title":"Innovación",
"questions":[
{"id":"q38","text":"Ecodiseño"},
{"id":"q39","text":"Productos certificados"},
{"id":"q40","text":"I+D sostenible"},
{"id":"q41","text":"Packaging reciclable"}
]
},

{
"id":10,
"title":"Comunidades",
"questions":[
{"id":"q42","text":"Impacto social"},
{"id":"q43","text":"Inversión social"},
{"id":"q44","text":"Consulta comunidades"},
{"id":"q45","text":"Inclusión laboral"}
]
},

{
"id":11,
"title":"Cumplimiento",
"questions":[
{"id":"q46","text":"Sanciones"},
{"id":"q47","text":"Riesgos ESG"},
{"id":"q48","text":"Certificaciones"},
{"id":"q49","text":"Permisos ambientales"},
{"id":"q50","text":"Materialidad"}
]
},

{
"id":12,
"title":"Digitalización",
"questions":[
{"id":"q51","text":"ISO 27001"},
{"id":"q52","text":"Ciberseguridad"},
{"id":"q53","text":"Privacidad datos"}
]
},

{
"id":13,
"title":"Finanzas Sostenibles",
"questions":[
{"id":"q54","text":"Bonos verdes"},
{"id":"q55","text":"Pasivos ambientales"},
{"id":"q56","text":"Estándares reporte"},
{"id":"q57","text":"Doble materialidad"}
]
},

{
"id":14,
"title":"Estrategia ESG",
"questions":[
{"id":"q58","text":"KPIs ESG"},
{"id":"q59","text":"Remuneración ESG"},
{"id":"q60","text":"Barreras sostenibilidad"}
]
}

]

# =========================
# GENERADOR PDF
# =========================

def generate_pdf(data):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Diagnóstico ESG", styles["Title"]))
    elements.append(Spacer(1,20))

    for section in SECTIONS:

        elements.append(
            Paragraph(
                f"{section['id']}. {section['title']}",
                styles["Heading2"]
            )
        )

        for q in section["questions"]:

            answer = data.get(q["id"], "Sin respuesta")

            elements.append(
                Paragraph(q["text"], styles["Heading4"])
            )

            elements.append(
                Paragraph(f"Respuesta: {answer}", styles["Normal"])
            )

            elements.append(Spacer(1,10))

    doc.build(elements)

    buffer.seek(0)
    return buffer


# =========================
# HOME
# =========================

@app.route("/")
def index():
    return render_template("index.html", sections=SECTIONS)


# =========================
# SUBMIT
# =========================

@app.route("/submit", methods=["POST"])
def submit():

    try:

        data = request.get_json(force=True)

        answers = data.get("answers", {})

        pdf = generate_pdf(answers)

        return send_file(
            pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="diagnostico_esg.pdf"
        )

    except Exception as e:
        print("ERROR REAL:", e)
        return jsonify({"error": str(e)}), 500


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
