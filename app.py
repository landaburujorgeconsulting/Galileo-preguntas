from flask import Flask, render_template, request, jsonify, send_file as flask_send_file
import io
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
import os




from datetime import datetime

app = Flask(__name__)

SECTIONS = [
    {
        "id": 1,
        "title": "Gobernanza Corporativa y Etica",
        "subtitle": "GRI 2-9 | ISO 26000 | ESRS G1",
        "questions": [
            {"id": "q1", "text": "Su organizacion cuenta con un Codigo de Etica o Conducta formalmente aprobado por la alta direccion?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q2", "text": "Dispone de una politica antisoborno y anticorrupcion documentada y comunicada a todo el personal?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q3", "text": "Existe un canal de denuncias (whistleblower) confidencial disponible para empleados y partes interesadas externas?", "type": "options", "options": ["Si", "No"]},
            {"id": "q4", "text": "En los ultimos 3 anos se registraron casos confirmados de corrupcion, soborno o conducta antietica? En caso afirmativo, como se gestionaron?", "type": "open", "placeholder": "Describa la situacion..."},
            {"id": "q5", "text": "Su empresa publica un informe de sostenibilidad o RSE anual, verificado por terceros?", "type": "options", "options": ["Si", "No", "En proceso"]},
        ]
    },
    {
        "id": 2,
        "title": "Derechos Humanos y Condiciones Laborales",
        "subtitle": "UNGPs | GRI 408/409 | ESRS S1 | OIT",
        "questions": [
            {"id": "q6", "text": "Cuenta con una politica de derechos humanos alineada con los Principios Rectores de la ONU (UNGPs)?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q7", "text": "Realiza procesos de debida diligencia en derechos humanos en su cadena de valor?", "type": "options", "options": ["Si", "No", "En proceso"]},
            {"id": "q8", "text": "Garantiza el pago de un salario digno (living wage) a todos sus trabajadores, incluyendo subcontratistas directos?", "type": "options", "options": ["Si", "No", "Parcialmente"]},
            {"id": "q9", "text": "Permite y respeta la libertad de asociacion sindical y la negociacion colectiva de sus empleados?", "type": "options", "options": ["Si", "No", "No aplica"]},
            {"id": "q10", "text": "Tiene implementadas politicas para prevenir y gestionar el trabajo infantil y el trabajo forzoso?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q11", "text": "Cual es la tasa de rotacion de personal voluntaria en el ultimo ano fiscal?", "type": "open", "placeholder": "Indique el porcentaje (%)"},
            {"id": "q12", "text": "Dispone de programas formales de capacitacion y desarrollo profesional para sus empleados?", "type": "open", "placeholder": "Si / No + Horas promedio por ano"},
            {"id": "q13", "text": "Cuenta con politica de no discriminacion e igualdad de oportunidades? Incluye diversidad de genero, etnia y discapacidad?", "type": "options", "options": ["Si", "No", "Parcialmente"]},
        ]
    },
    {
        "id": 3,
        "title": "Salud y Seguridad Ocupacional",
        "subtitle": "ISO 45001 | GRI 403 | ESRS S1-14",
        "questions": [
            {"id": "q14", "text": "Cuenta con un Sistema de Gestion de Seguridad y Salud en el Trabajo (SST) certificado o en proceso de certificacion?", "type": "options", "options": ["Certificado", "En proceso", "No tiene"]},
            {"id": "q15", "text": "Indique su tasa de lesiones registrables (TRIR) y tasa de dias perdidos (LTIFR) del ultimo ano.", "type": "open", "placeholder": "Ej: TRIR: 2.3 | LTIFR: 0.8"},
            {"id": "q16", "text": "Se realizan simulacros de emergencia y programas de bienestar (salud mental, ergonomia) para los trabajadores?", "type": "options", "options": ["Si", "No", "Parcialmente"]},
        ]
    },
    {
        "id": 4,
        "title": "Medio Ambiente - Cambio Climatico y Energia",
        "subtitle": "GRI 302/305 | TCFD | ESRS E1 | SBTi",
        "questions": [
            {"id": "q17", "text": "Ha realizado un inventario de gases de efecto invernadero (GEI) de Alcances 1 y 2? Incluye Alcance 3?", "type": "options", "options": ["Si (todos)", "Solo 1-2", "No"]},
            {"id": "q18", "text": "Cual fue su consumo total de energia en el ultimo ano (MWh) y que porcentaje proviene de fuentes renovables?", "type": "open", "placeholder": "Ej: 5.200 MWh / 35% renovable"},
            {"id": "q19", "text": "Tiene metas de reduccion de emisiones GEI validadas por Science Based Targets initiative (SBTi) u otro estandar equivalente?", "type": "options", "options": ["Si (SBTi)", "Si (otro)", "En proceso", "No"]},
            {"id": "q20", "text": "Ha realizado analisis de riesgos climaticos fisicos y de transicion sobre sus operaciones y cadena de suministro?", "type": "options", "options": ["Si", "En proceso", "No"]},
            {"id": "q21", "text": "Cuenta con programa de eficiencia energetica activo con metas medibles y seguimiento periodico?", "type": "open", "placeholder": "Si / No + descripcion de metas"},
        ]
    },
    {
        "id": 5,
        "title": "Medio Ambiente - Agua y Biodiversidad",
        "subtitle": "GRI 303/304 | TNFD | ESRS E3/E4",
        "questions": [
            {"id": "q22", "text": "Cual fue el volumen total de agua extraida (m3) en el ultimo ano? Diferencia por fuente (superficial, subterranea, municipal)?", "type": "open", "placeholder": "Ej: 12.000 m3 total - 60% subterranea / 40% municipal"},
            {"id": "q23", "text": "Sus instalaciones se ubican en zonas de estres hidrico alto o muy alto segun WRI Aqueduct u herramienta equivalente?", "type": "options", "options": ["Si", "No", "Evaluacion en curso"]},
            {"id": "q24", "text": "Cuenta con politica de proteccion de la biodiversidad y realiza evaluaciones de impacto en ecosistemas?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
        ]
    },
    {
        "id": 6,
        "title": "Medio Ambiente - Residuos y Economia Circular",
        "subtitle": "GRI 306 | ESRS E5 | ISO 14001",
        "questions": [
            {"id": "q25", "text": "Cuantas toneladas de residuos genero en el ultimo ano? Indique el desglose: peligrosos, no peligrosos, reciclados.", "type": "open", "placeholder": "Ej: 320 ton total - 15 peligrosos / 200 reciclados / 105 disposicion final"},
            {"id": "q26", "text": "Tiene implementada una estrategia de economia circular (diseno para el desmontaje, reutilizacion, remanufactura)?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q27", "text": "Ha implementado medidas especificas para reducir el uso de plasticos de un solo uso en sus productos o embalajes?", "type": "options", "options": ["Si", "No", "En proceso"]},
        ]
    },
    {
        "id": 7,
        "title": "Cadena de Suministro Sostenible",
        "subtitle": "ISO 20400 | GRI 2-6 | ESRS G1-4",
        "questions": [
            {"id": "q28", "text": "Cuenta con una politica de compras sostenibles que incorpore criterios ESG (ambiental, social, gobernanza)?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q29", "text": "Aplica criterios de sostenibilidad en la seleccion y evaluacion periodica de sus propios proveedores?", "type": "open", "placeholder": "Si / No + porcentaje evaluado"},
            {"id": "q30", "text": "Que porcentaje de su gasto en compras corresponde a proveedores locales (dentro de un radio de 150 km o en la misma region)?", "type": "open", "placeholder": "Indique el porcentaje (%)"},
            {"id": "q31", "text": "Realiza auditorias de sostenibilidad o visitas a instalaciones de sus proveedores criticos?", "type": "open", "placeholder": "Si / No + frecuencia"},
            {"id": "q32", "text": "Exige a sus proveedores estrategicos la firma de un Codigo de Conducta de Proveedores con requisitos ESG?", "type": "options", "options": ["Si", "No"]},
            {"id": "q33", "text": "Tiene programa de desarrollo de capacidades ESG (formacion, asistencia tecnica) para sus proveedores PYME?", "type": "options", "options": ["Si", "No"]},
            {"id": "q34", "text": "Sus contratos con proveedores incluyen clausulas de sostenibilidad, penalizaciones o incentivos por desempeno ESG?", "type": "options", "options": ["Si", "No", "En implementacion"]},
        ]
    },
    {
        "id": 8,
        "title": "Minerales y Materiales Criticos",
        "subtitle": "Dodd-Frank Sec. 1502 | OECD DDG | GRI 3-3",
        "questions": [
            {"id": "q35", "text": "Utiliza minerales de zonas de conflicto (3TG: estano, tantalo, tungsteno, oro) en sus productos o procesos?", "type": "options", "options": ["Si", "No", "Bajo evaluacion"]},
            {"id": "q36", "text": "Puede rastrear el origen de sus materias primas criticas hasta el extractor o productor primario (trazabilidad)?", "type": "options", "options": ["Si (completo)", "Parcialmente", "No"]},
            {"id": "q37", "text": "Que porcentaje de los materiales utilizados en sus productos son reciclados o de origen secundario?", "type": "open", "placeholder": "Indique el porcentaje (%)"},
        ]
    },
    {
        "id": 9,
        "title": "Innovacion, Productos y Servicios Sostenibles",
        "subtitle": "GRI 301 | ESRS E5 | ISO 14006",
        "questions": [
            {"id": "q38", "text": "Incorpora criterios de ecodiseno (analisis de ciclo de vida, durabilidad, reparabilidad) en el desarrollo de sus productos?", "type": "options", "options": ["Si", "No", "En proceso"]},
            {"id": "q39", "text": "Que porcentaje de su portafolio de productos esta etiquetado con certificacion ambiental o social reconocida?", "type": "open", "placeholder": "Indique el porcentaje (%)"},
            {"id": "q40", "text": "Invierte en I+D orientada a soluciones de sostenibilidad o transicion verde? Cual es el % del presupuesto de I+D destinado a esto?", "type": "open", "placeholder": "Si / No + % I+D"},
            {"id": "q41", "text": "Sus embalajes y materiales de marketing son 100% reciclables, compostables o reutilizables?", "type": "options", "options": ["Si", "No", "En transicion"]},
        ]
    },
    {
        "id": 10,
        "title": "Comunidades y Valor Social",
        "subtitle": "GRI 413 | UNGPs | ESRS S3",
        "questions": [
            {"id": "q42", "text": "Realiza evaluaciones de impacto en las comunidades donde opera (ESIA)?", "type": "options", "options": ["Si", "No", "En proceso"]},
            {"id": "q43", "text": "Tiene programas de inversion social comunitaria activos? Indique el monto invertido y numero de beneficiarios.", "type": "open", "placeholder": "Si / No + datos cuantitativos"},
            {"id": "q44", "text": "Dispone de mecanismos formales de consulta y participacion de comunidades indigenas o en situacion de vulnerabilidad?", "type": "options", "options": ["Si", "No", "No aplica"]},
            {"id": "q45", "text": "Tiene politica activa de fomento a la contratacion de poblacion vulnerable (personas con discapacidad, jovenes, mujeres)?", "type": "open", "placeholder": "Si / No + % en plantilla"},
        ]
    },
    {
        "id": 11,
        "title": "Cumplimiento Legal y Gestion de Riesgos ESG",
        "subtitle": "GRI 2-27 | ISO 31000 | ESRS G1",
        "questions": [
            {"id": "q46", "text": "Ha recibido sanciones, multas o incumplimientos regulatorios ambientales o laborales en los ultimos 3 anos?", "type": "open", "placeholder": "Si / No + descripcion"},
            {"id": "q47", "text": "Su organizacion cuenta con un sistema formal de identificacion, evaluacion y gestion de riesgos ESG integrado al ERM corporativo?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q48", "text": "Posee certificaciones ambientales vigentes (ISO 14001, EMAS, LEED, similar)? Indique cuales y sus fechas de vencimiento.", "type": "open", "placeholder": "Si + listado / No"},
            {"id": "q49", "text": "Tiene identificados y mapeados todos los permisos ambientales vigentes necesarios para sus operaciones?", "type": "options", "options": ["Si", "No", "Parcialmente"]},
            {"id": "q50", "text": "Realiza ejercicios periodicos de materialidad ESG para priorizar sus temas de sostenibilidad mas relevantes?", "type": "open", "placeholder": "Si / No + frecuencia"},
        ]
    },
    {
        "id": 12,
        "title": "Digitalizacion, Datos y Privacidad",
        "subtitle": "ISO 27001 | GRI 418 | ESRS G1",
        "questions": [
            {"id": "q51", "text": "Cuenta con una politica de seguridad de la informacion certificada o alineada a la norma ISO 27001?", "type": "options", "options": ["Certificado", "Alineado", "No tiene"]},
            {"id": "q52", "text": "Ha sufrido incidentes de ciberseguridad o filtraciones de datos personales en los ultimos 3 anos? Como fueron gestionados?", "type": "open", "placeholder": "Si / No + descripcion"},
            {"id": "q53", "text": "Tiene implementado un programa de privacidad de datos (Privacy by Design) y gestion del ciclo de vida de los datos personales?", "type": "options", "options": ["Si", "No", "En implementacion"]},
        ]
    },
    {
        "id": 13,
        "title": "Finanzas Sostenibles y Reporte",
        "subtitle": "GRI 201 | TCFD | ESRS E1 | SASB",
        "questions": [
            {"id": "q54", "text": "Ha emitido instrumentos de deuda sostenible (bonos verdes, bonos sociales, bonos vinculados a sostenibilidad)?", "type": "open", "placeholder": "Si + monto / No / En evaluacion"},
            {"id": "q55", "text": "Sus estados financieros incorporan la valoracion de pasivos ambientales o riesgos climaticos?", "type": "options", "options": ["Si", "No", "En proceso"]},
            {"id": "q56", "text": "Utiliza estandares GRI, SASB, TCFD, TNFD o ESRS para la elaboracion de sus reportes de sostenibilidad?", "type": "open", "placeholder": "Indique cuales estandares utiliza"},
            {"id": "q57", "text": "Ha realizado una evaluacion de doble materialidad (impactos de adentro hacia afuera y de afuera hacia adentro)?", "type": "options", "options": ["Si", "No", "En proceso"]},
        ]
    },
    {
        "id": 14,
        "title": "Estrategia y Compromiso de Alta Direccion",
        "subtitle": "GRI 2-9/2-22 | ESRS G1 | TCFD Governance",
        "questions": [
            {"id": "q58", "text": "La estrategia corporativa tiene metas ESG integradas con KPI y horizonte temporal definido?", "type": "options", "options": ["Si", "No", "En desarrollo"]},
            {"id": "q59", "text": "La remuneracion variable de la alta direccion esta vinculada al cumplimiento de objetivos de sostenibilidad?", "type": "options", "options": ["Si", "No", "Parcialmente"]},
            {"id": "q60", "text": "Cual es la principal barrera que enfrenta su organizacion para avanzar en sostenibilidad, y que apoyo requeriria de sus clientes/compradores para superarla?", "type": "open", "placeholder": "Describa libremente la situacion..."},
        ]
    },
]


import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


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
    story = []

    # CONTENIDO PDF
    story.append(Paragraph("Informe de Sostenibilidad", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Empresa: {company_name}", styles["Normal"]))
    story.append(Paragraph(f"Contacto: {contact_name}", styles["Normal"]))
    story.append(Paragraph(f"Email: {contact_email}", styles["Normal"]))

    story.append(Spacer(1, 20))

    for key, value in form_data.items():
        story.append(Paragraph(f"{key}: {value}", styles["Normal"]))

    # 🔥 ESTA LINEA ERA TU ERROR
    doc.build(story)

    buffer.seek(0)

    return buffer

    buffer.seek(0)
    return buffer
    MILITARY_GREEN = colors.HexColor("#3D5A3E")
    DARK_GREEN = colors.HexColor("#1E3320")
    LIGHT_GREEN = colors.HexColor("#6B8F6B")
    ACCENT = colors.HexColor("#A8C5A0")
    BG_LIGHT = colors.HexColor("#F5F7F5")
    TEXT_DARK = colors.HexColor("#1A2E1A")
    TEXT_GRAY = colors.HexColor("#5A6B5A")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18,
        textColor=colors.white, alignment=TA_CENTER, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=2
    )
    section_title_style = ParagraphStyle(
        'SectionTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11,
        textColor=colors.white, spaceAfter=2
    )
    section_sub_style = ParagraphStyle(
        'SectionSub', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8,
        textColor=ACCENT, spaceAfter=0
    )
    question_style = ParagraphStyle(
        'Question', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9,
        textColor=TEXT_DARK, spaceBefore=6, spaceAfter=3
    )
    answer_style = ParagraphStyle(
        'Answer', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        textColor=TEXT_GRAY, leftIndent=10, spaceAfter=4
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        textColor=TEXT_DARK, spaceAfter=3
    )

    elements = []

    header_data = [[Paragraph("DIAGNOSTICO DE SOSTENIBILIDAD PARA PROVEEDORES", title_style)]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), MILITARY_GREEN),
        ('ROWPADDING', (0, 0), (-1, -1), 16),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)

    sub_data = [[Paragraph("60 preguntas | GRI - ISO 20400 - UNGPs - TCFD - ESRS - ISO 45001 - ISO 14001", subtitle_style)]]
    sub_table = Table(sub_data, colWidths=[17*cm])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_GREEN),
        ('ROWPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 0.5*cm))

    meta_data = [
        [Paragraph(f"<b>Empresa:</b> {company_name}", meta_style),
         Paragraph(f"<b>Contacto:</b> {contact_name}", meta_style)],
        [Paragraph(f"<b>Email:</b> {contact_email}", meta_style),
         Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", meta_style)],
    ]
    meta_table = Table(meta_data, colWidths=[8.5*cm, 8.5*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('ROWPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, -1), (-1, -1), 1, LIGHT_GREEN),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.5*cm))

    for section in SECTIONS:
        sec_header = [[
            Paragraph(f"{section['id']}. {section['title']}", section_title_style),
            Paragraph(section['subtitle'], section_sub_style)
        ]]
        sec_table = Table(sec_header, colWidths=[17*cm])
        sec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), MILITARY_GREEN),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('TOPPADDING', (0, 1), (-1, 1), 0),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
        ]))
        elements.append(sec_table)

        for q in section['questions']:
            elements.append(Paragraph(f"- {q['text']}", question_style))
            answer = form_data.get(q['id'], "")
            if not answer:
                answer = "Sin respuesta"
            elements.append(Paragraph(f"Respuesta: {answer}", answer_style))

        elements.append(Spacer(1, 0.3*cm))

    footer_data = [[
        Paragraph(
            "Diagnostico gestionado a traves de la plataforma GALILEO · Uso confidencial exclusivo para evaluacion ESG",
            ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica',
                           fontSize=8, textColor=colors.white, alignment=TA_CENTER)
        )
    ]]
    footer_table = Table(footer_data, colWidths=[17*cm])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_GREEN),
        ('ROWPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def send_email(pdf_bytes, company_name, contact_email):
    sender_email = os.environ.get("MAIL_USER", "")
    sender_password = os.environ.get("MAIL_PASS", "")
    recipient = "nodoconsultoria2015@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = f"Diagnostico ESG GALILEO - {company_name}"

    body = (
        f"Se ha recibido un nuevo Diagnostico de Sostenibilidad ESG a traves de la plataforma GALILEO.\n\n"
        f"Empresa: {company_name}\n"
        f"Contacto: {contact_email}\n"
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        f"Adjunto encontrara el informe completo en formato PDF.\n\n"
        f"Plataforma GALILEO | Diagnostico ESG para Proveedores"
    )
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    filename = f"diagnostico_esg_{company_name.replace(' ', '_')}.pdf"
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())


@app.route('/')
def index():
    return render_template('index.html', sections=SECTIONS)


@app.route('/submit', methods=['POST'])
def submit():

    try:
        data = request.json

        company_name = data.get("company_name", "")
        contact_name = data.get("contact_name", "")
        contact_email = data.get("contact_email", "")
        form_data = data.get("answers", {})

        pdf_buffer = generate_pdf(
            form_data,
            company_name,
            contact_name,
            contact_email
        )

        return flask_send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="diagnostico_sostenibilidad.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("ERROR REAL:", e)
        return jsonify({"error": str(e)}), 500


        import io

       

   
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
