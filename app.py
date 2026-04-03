SECTIONS = [
{
"id": 1,
"title": "Gobernanza y Ética",
"questions": [
{
"id": "q1",
"text": "¿Su organización cuenta con un Código de Ética?"
},
{
"id": "q2",
"text": "¿Dispone de política antisoborno?"
}
]
},

from flask import Flask, render_template, request, jsonify, send_file
import io
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

app = Flask(__name__)

app = Flask(__name__)

# ===============================
# DIAGNOSTICO ESG - SECCIONES
# ===============================

SECTIONS = [

# -------------------------------------------------
# 1. GOBERNANZA Y ETICA
# -------------------------------------------------
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



# -------------------------------------------------
# 2. DERECHOS HUMANOS
# -------------------------------------------------
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

# -------------------------------------------------
# 3. SALUD Y SEGURIDAD
# -------------------------------------------------
{
"id":3,
"title":"Salud y Seguridad Ocupacional",
"questions":[
{"id":"q14","text":"Sistema SST certificado"},
{"id":"q15","text":"TRIR y LTIFR último año"},
{"id":"q16","text":"Simulacros y bienestar laboral"}
]
},

# -------------------------------------------------
# 4. CAMBIO CLIMATICO
# -------------------------------------------------
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
},

# -------------------------------------------------
# 5. AGUA Y BIODIVERSIDAD
# -------------------------------------------------
{
"id":5,
"title":"Agua y Biodiversidad",
"questions":[
{"id":"q22","text":"Consumo total de agua"},
{"id":"q23","text":"Operación en zonas estrés hídrico"},
{"id":"q24","text":"Política biodiversidad"}
]
},

# -------------------------------------------------
# 6. RESIDUOS
# -------------------------------------------------
{
"id":6,
"title":"Residuos y Economía Circular",
"questions":[
{"id":"q25","text":"Toneladas de residuos generados"},
{"id":"q26","text":"Estrategia economía circular"},
{"id":"q27","text":"Reducción plásticos"}
]
},

# -------------------------------------------------
# 7. CADENA DE SUMINISTRO
# -------------------------------------------------
{
"id":7,
"title":"Cadena de Suministro Sostenible",
"questions":[
{"id":"q28","text":"Política compras sostenibles"},
{"id":"q29","text":"Evaluación ESG proveedores"},
{"id":"q30","text":"% compras locales"},
{"id":"q31","text":"Auditorías a proveedores"},
{"id":"q32","text":"Código conducta proveedores"},
{"id":"q33","text":"Programa desarrollo PYME"},
{"id":"q34","text":"Cláusulas ESG contractuales"}
]
},

# -------------------------------------------------
# 8. MINERALES
# -------------------------------------------------
{
"id":8,
"title":"Minerales y Materiales Críticos",
"questions":[
{"id":"q35","text":"Uso minerales conflicto"},
{"id":"q36","text":"Trazabilidad materias primas"},
{"id":"q37","text":"% material reciclado"}
]
},

# -------------------------------------------------
# 9. INNOVACION
# -------------------------------------------------
{
"id":9,
"title":"Innovación y Productos Sostenibles",
"questions":[
{"id":"q38","text":"Ecodiseño"},
{"id":"q39","text":"% productos certificados"},
{"id":"q40","text":"I+D sostenible"},
{"id":"q41","text":"Packaging reciclable"}
]
},

# -------------------------------------------------
# 10. COMUNIDADES
# -------------------------------------------------
{
"id":10,
"title":"Comunidades y Valor Social",
"questions":[
{"id":"q42","text":"Evaluaciones impacto social"},
{"id":"q43","text":"Inversión social"},
{"id":"q44","text":"Consulta comunidades"},
{"id":"q45","text":"Contratación población vulnerable"}
]
},

# -------------------------------------------------
# 11. CUMPLIMIENTO
# -------------------------------------------------
{
"id":11,
"title":"Cumplimiento Legal y Riesgos ESG",
"questions":[
{"id":"q46","text":"Sanciones regulatorias"},
{"id":"q47","text":"Sistema gestión riesgos ESG"},
{"id":"q48","text":"Certificaciones ambientales"},
{"id":"q49","text":"Permisos ambientales"},
{"id":"q50","text":"Ejercicios materialidad"}
]
},

# -------------------------------------------------
# 12. DIGITALIZACION
# -------------------------------------------------
{
"id":12,
"title":"Digitalización y Privacidad",
"questions":[
{"id":"q51","text":"Seguridad información ISO 27001"},
{"id":"q52","text":"Incidentes ciberseguridad"},
{"id":"q53","text":"Programa privacidad datos"}
]
},

# -------------------------------------------------
# 13. FINANZAS SOSTENIBLES
# -------------------------------------------------
{
"id":13,
"title":"Finanzas Sostenibles",
"questions":[
{"id":"q54","text":"Bonos verdes o sostenibles"},
{"id":"q55","text":"Pasivos ambientales en estados financieros"},
{"id":"q56","text":"Estándares reporte utilizados"},
{"id":"q57","text":"Evaluación doble materialidad"}
]
},

# -------------------------------------------------
# 14. ESTRATEGIA ESG
# -------------------------------------------------
{
"id":14,
"title":"Estrategia y Alta Dirección",
"questions":[
{"id":"q58","text":"KPIs ESG integrados"},
{"id":"q59","text":"Remuneración vinculada ESG"},
{"id":"q60","text":"Principal barrera sostenibilidad"}
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
