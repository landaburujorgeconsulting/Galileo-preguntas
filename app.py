from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import io
import os
from datetime import datetime

app = Flask(__name__)

SECTIONS = [
    {
        "id": 1,
        "title": "Gobernanza Corporativa y Ética",
        "subtitle": "GRI 2-9 | ISO 26000 § 6.6 | ESRS G1",
        "questions": [
            {
                "id": "q1",
                "text": "¿Su organización cuenta con un Código de Ética o Conducta formalmente aprobado por la alta dirección?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q2",
                "text": "¿Dispone de una política antisoborno y anticorrupción documentada y comunicada a todo el personal?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q3",
                "text": "¿Existe un canal de denuncias (whistleblower) confidencial disponible para empleados y partes interesadas externas?",
                "type": "options",
                "options": ["Sí", "No"]
            },
            {
                "id": "q4",
                "text": "¿En los últimos 3 años se registraron casos confirmados de corrupción, soborno o conducta antiética? En caso afirmativo, ¿cómo se gestionaron?",
                "type": "open"
            },
            {
                "id": "q5",
                "text": "¿Su empresa publica un informe de sostenibilidad o RSE anual, verificado por terceros?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
        ]
    },
    {
        "id": 2,
        "title": "Derechos Humanos y Condiciones Laborales",
        "subtitle": "UNGPs | GRI 408/409 | ESRS S1 | OIT",
        "questions": [
            {
                "id": "q6",
                "text": "¿Cuenta con una política de derechos humanos alineada con los Principios Rectores de la ONU (UNGPs)?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q7",
                "text": "¿Realiza procesos de debida diligencia en derechos humanos en su cadena de valor?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
            {
                "id": "q8",
                "text": "¿Garantiza el pago de un salario digno (living wage) a todos sus trabajadores, incluyendo subcontratistas directos?",
                "type": "options",
                "options": ["Sí", "No", "Parcialmente"]
            },
            {
                "id": "q9",
                "text": "¿Permite y respeta la libertad de asociación sindical y la negociación colectiva de sus empleados?",
                "type": "options",
                "options": ["Sí", "No", "No aplica"]
            },
            {
                "id": "q10",
                "text": "¿Tiene implementadas políticas para prevenir y gestionar el trabajo infantil y el trabajo forzoso?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q11",
                "text": "¿Cuál es la tasa de rotación de personal voluntaria en el último año fiscal?",
                "type": "open",
                "placeholder": "Indique el porcentaje (%)"
            },
            {
                "id": "q12",
                "text": "¿Dispone de programas formales de capacitación y desarrollo profesional para sus empleados?",
                "type": "open",
                "placeholder": "Sí / No + Horas promedio por año"
            },
            {
                "id": "q13",
                "text": "¿Cuenta con política de no discriminación e igualdad de oportunidades? ¿Incluye diversidad de género, etnia y discapacidad?",
                "type": "options",
                "options": ["Sí", "No", "Parcialmente"]
            },
        ]
    },
    {
        "id": 3,
        "title": "Salud y Seguridad Ocupacional",
        "subtitle": "ISO 45001 | GRI 403 | ESRS S1-14",
        "questions": [
            {
                "id": "q14",
                "text": "¿Cuenta con un Sistema de Gestión de Seguridad y Salud en el Trabajo (SST) certificado o en proceso de certificación?",
                "type": "options",
                "options": ["Certificado", "En proceso", "No tiene"]
            },
            {
                "id": "q15",
                "text": "Indique su tasa de lesiones registrables (TRIR) y tasa de días perdidos (LTIFR) del último año.",
                "type": "open",
                "placeholder": "Ej: TRIR: 2.3 | LTIFR: 0.8"
            },
            {
                "id": "q16",
                "text": "¿Se realizan simulacros de emergencia y programas de bienestar (salud mental, ergonomía) para los trabajadores?",
                "type": "options",
                "options": ["Sí", "No", "Parcialmente"]
            },
        ]
    },
    {
        "id": 4,
        "title": "Medio Ambiente – Cambio Climático y Energía",
        "subtitle": "GRI 302/305 | TCFD | ESRS E1 | SBTi",
        "questions": [
            {
                "id": "q17",
                "text": "¿Ha realizado un inventario de gases de efecto invernadero (GEI) de Alcances 1 y 2? ¿Incluye Alcance 3?",
                "type": "options",
                "options": ["Sí (todos)", "Solo 1-2", "No"]
            },
            {
                "id": "q18",
                "text": "¿Cuál fue su consumo total de energía en el último año (MWh) y qué porcentaje proviene de fuentes renovables?",
                "type": "open",
                "placeholder": "Ej: 5.200 MWh / 35% renovable"
            },
            {
                "id": "q19",
                "text": "¿Tiene metas de reducción de emisiones GEI validadas por Science Based Targets initiative (SBTi) u otro estándar equivalente?",
                "type": "options",
                "options": ["Sí (SBTi)", "Sí (otro)", "En proceso", "No"]
            },
            {
                "id": "q20",
                "text": "¿Ha realizado análisis de riesgos climáticos físicos y de transición sobre sus operaciones y cadena de suministro?",
                "type": "options",
                "options": ["Sí", "En proceso", "No"]
            },
            {
                "id": "q21",
                "text": "¿Cuenta con programa de eficiencia energética activo con metas medibles y seguimiento periódico?",
                "type": "open",
                "placeholder": "Sí / No + descripción de metas"
            },
        ]
    },
    {
        "id": 5,
        "title": "Medio Ambiente – Agua y Biodiversidad",
        "subtitle": "GRI 303/304 | TNFD | ESRS E3/E4",
        "questions": [
            {
                "id": "q22",
                "text": "¿Cuál fue el volumen total de agua extraída (m³) en el último año? ¿Diferencia por fuente (superficial, subterránea, municipal)?",
                "type": "open",
                "placeholder": "Ej: 12.000 m³ total – 60% subterránea / 40% municipal"
            },
            {
                "id": "q23",
                "text": "¿Sus instalaciones se ubican en zonas de estrés hídrico alto o muy alto según WRI Aqueduct u herramienta equivalente?",
                "type": "options",
                "options": ["Sí", "No", "Evaluación en curso"]
            },
            {
                "id": "q24",
                "text": "¿Cuenta con política de protección de la biodiversidad y realiza evaluaciones de impacto en ecosistemas?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
        ]
    },
    {
        "id": 6,
        "title": "Medio Ambiente – Residuos y Economía Circular",
        "subtitle": "GRI 306 | ESRS E5 | ISO 14001",
        "questions": [
            {
                "id": "q25",
                "text": "¿Cuántas toneladas de residuos generó en el último año? Indique el desglose: peligrosos, no peligrosos, reciclados.",
                "type": "open",
                "placeholder": "Ej: 320 ton total – 15 peligrosos / 200 reciclados / 105 disposición final"
            },
            {
                "id": "q26",
                "text": "¿Tiene implementada una estrategia de economía circular (diseño para el desmontaje, reutilización, remanufactura)?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q27",
                "text": "¿Ha implementado medidas específicas para reducir el uso de plásticos de un solo uso en sus productos o embalajes?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
        ]
    },
    {
        "id": 7,
        "title": "Cadena de Suministro Sostenible",
        "subtitle": "ISO 20400 | GRI 2-6 | ESRS G1-4",
        "questions": [
            {
                "id": "q28",
                "text": "¿Cuenta con una política de compras sostenibles que incorpore criterios ESG (ambiental, social, gobernanza)?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q29",
                "text": "¿Aplica criterios de sostenibilidad en la selección y evaluación periódica de sus propios proveedores?",
                "type": "open",
                "placeholder": "Sí / No + porcentaje evaluado"
            },
            {
                "id": "q30",
                "text": "¿Qué porcentaje de su gasto en compras corresponde a proveedores locales (dentro de un radio de 150 km o en la misma región)?",
                "type": "open",
                "placeholder": "Indique el porcentaje (%)"
            },
            {
                "id": "q31",
                "text": "¿Realiza auditorías de sostenibilidad o visitas a instalaciones de sus proveedores críticos?",
                "type": "open",
                "placeholder": "Sí / No + frecuencia"
            },
            {
                "id": "q32",
                "text": "¿Exige a sus proveedores estratégicos la firma de un Código de Conducta de Proveedores con requisitos ESG?",
                "type": "options",
                "options": ["Sí", "No"]
            },
            {
                "id": "q33",
                "text": "¿Tiene programa de desarrollo de capacidades ESG (formación, asistencia técnica) para sus proveedores PYME?",
                "type": "options",
                "options": ["Sí", "No"]
            },
            {
                "id": "q34",
                "text": "¿Sus contratos con proveedores incluyen cláusulas de sostenibilidad, penalizaciones o incentivos por desempeño ESG?",
                "type": "options",
                "options": ["Sí", "No", "En implementación"]
            },
        ]
    },
    {
        "id": 8,
        "title": "Minerales y Materiales Críticos",
        "subtitle": "Dodd-Frank Sec. 1502 | OECD DDG | GRI 3-3",
        "questions": [
            {
                "id": "q35",
                "text": "¿Utiliza minerales de zonas de conflicto (3TG: estaño, tántalo, tungsteno, oro) en sus productos o procesos?",
                "type": "options",
                "options": ["Sí", "No", "Bajo evaluación"]
            },
            {
                "id": "q36",
                "text": "¿Puede rastrear el origen de sus materias primas críticas hasta el extractor o productor primario (trazabilidad)?",
                "type": "options",
                "options": ["Sí (completo)", "Parcialmente", "No"]
            },
            {
                "id": "q37",
                "text": "¿Qué porcentaje de los materiales utilizados en sus productos son reciclados o de origen secundario?",
                "type": "open",
                "placeholder": "Indique el porcentaje (%)"
            },
        ]
    },
    {
        "id": 9,
        "title": "Innovación, Productos y Servicios Sostenibles",
        "subtitle": "GRI 301 | ESRS E5 | ISO 14006",
        "questions": [
            {
                "id": "q38",
                "text": "¿Incorpora criterios de ecodiseño (análisis de ciclo de vida, durabilidad, reparabilidad) en el desarrollo de sus productos?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
            {
                "id": "q39",
                "text": "¿Qué porcentaje de su portafolio de productos está etiquetado con certificación ambiental o social reconocida?",
                "type": "open",
                "placeholder": "Indique el porcentaje (%)"
            },
            {
                "id": "q40",
                "text": "¿Invierte en I+D orientada a soluciones de sostenibilidad o transición verde? ¿Cuál es el % del presupuesto de I+D destinado a esto?",
                "type": "open",
                "placeholder": "Sí / No + % I+D"
            },
            {
                "id": "q41",
                "text": "¿Sus embalajes y materiales de marketing son 100% reciclables, compostables o reutilizables?",
                "type": "options",
                "options": ["Sí", "No", "En transición"]
            },
        ]
    },
    {
        "id": 10,
        "title": "Comunidades y Valor Social",
        "subtitle": "GRI 413 | UNGPs | ESRS S3",
        "questions": [
            {
                "id": "q42",
                "text": "¿Realiza evaluaciones de impacto en las comunidades donde opera (ESIA - Environmental and Social Impact Assessment)?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
            {
                "id": "q43",
                "text": "¿Tiene programas de inversión social comunitaria activos? Indique el monto invertido y número de beneficiarios.",
                "type": "open",
                "placeholder": "Sí / No + datos cuantitativos"
            },
            {
                "id": "q44",
                "text": "¿Dispone de mecanismos formales de consulta y participación de comunidades indígenas o en situación de vulnerabilidad?",
                "type": "options",
                "options": ["Sí", "No", "No aplica"]
            },
            {
                "id": "q45",
                "text": "¿Tiene política activa de fomento a la contratación de población vulnerable (personas con discapacidad, jóvenes, mujeres)?",
                "type": "open",
                "placeholder": "Sí / No + % en plantilla"
            },
        ]
    },
    {
        "id": 11,
        "title": "Cumplimiento Legal y Gestión de Riesgos ESG",
        "subtitle": "GRI 2-27 | ISO 31000 | ESRS G1",
        "questions": [
            {
                "id": "q46",
                "text": "¿Ha recibido sanciones, multas o incumplimientos regulatorios ambientales o laborales en los últimos 3 años?",
                "type": "open",
                "placeholder": "Sí / No + descripción"
            },
            {
                "id": "q47",
                "text": "¿Su organización cuenta con un sistema formal de identificación, evaluación y gestión de riesgos ESG integrado al ERM corporativo?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q48",
                "text": "¿Posee certificaciones ambientales vigentes (ISO 14001, EMAS, LEED, similar)? Indique cuáles y sus fechas de vencimiento.",
                "type": "open",
                "placeholder": "Sí + listado / No"
            },
            {
                "id": "q49",
                "text": "¿Tiene identificados y mapeados todos los permisos ambientales vigentes necesarios para sus operaciones?",
                "type": "options",
                "options": ["Sí", "No", "Parcialmente"]
            },
            {
                "id": "q50",
                "text": "¿Realiza ejercicios periódicos de materialidad ESG para priorizar sus temas de sostenibilidad más relevantes?",
                "type": "open",
                "placeholder": "Sí / No + frecuencia"
            },
        ]
    },
    {
        "id": 12,
        "title": "Digitalización, Datos y Privacidad",
        "subtitle": "ISO 27001 | GRI 418 | ESRS G1",
        "questions": [
            {
                "id": "q51",
                "text": "¿Cuenta con una política de seguridad de la información certificada o alineada a la norma ISO 27001?",
                "type": "options",
                "options": ["Certificado", "Alineado", "No tiene"]
            },
            {
                "id": "q52",
                "text": "¿Ha sufrido incidentes de ciberseguridad o filtraciones de datos personales en los últimos 3 años? ¿Cómo fueron gestionados?",
                "type": "open",
                "placeholder": "Sí / No + descripción"
            },
            {
                "id": "q53",
                "text": "¿Tiene implementado un programa de privacidad de datos (Privacy by Design) y gestión del ciclo de vida de los datos personales?",
                "type": "options",
                "options": ["Sí", "No", "En implementación"]
            },
        ]
    },
    {
        "id": 13,
        "title": "Finanzas Sostenibles y Reporte",
        "subtitle": "GRI 201 | TCFD | ESRS E1 | SASB",
        "questions": [
            {
                "id": "q54",
                "text": "¿Ha emitido instrumentos de deuda sostenible (bonos verdes, bonos sociales, bonos vinculados a sostenibilidad)?",
                "type": "open",
                "placeholder": "Sí + monto / No / En evaluación"
            },
            {
                "id": "q55",
                "text": "¿Sus estados financieros incorporan la valoración de pasivos ambientales o riesgos climáticos?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
            {
                "id": "q56",
                "text": "¿Utiliza estándares GRI, SASB, TCFD, TNFD o ESRS para la elaboración de sus reportes de sostenibilidad?",
                "type": "open",
                "placeholder": "Indique cuáles estándares utiliza"
            },
            {
                "id": "q57",
                "text": "¿Ha realizado una evaluación de doble materialidad (impactos de adentro hacia afuera y de afuera hacia adentro)?",
                "type": "options",
                "options": ["Sí", "No", "En proceso"]
            },
        ]
    },
    {
        "id": 14,
        "title": "Estrategia y Compromiso de Alta Dirección",
        "subtitle": "GRI 2-9/2-22 | ESRS G1 | TCFD Governance",
        "questions": [
            {
                "id": "q58",
                "text": "¿La estrategia corporativa tiene metas ESG integradas con KPI y horizonte temporal definido?",
                "type": "options",
                "options": ["Sí", "No", "En desarrollo"]
            },
            {
                "id": "q59",
                "text": "¿La remuneración variable de la alta dirección está vinculada al cumplimiento de objetivos de sostenibilidad?",
                "type": "options",
                "options": ["Sí", "No", "Parcialmente"]
            },
            {
                "id": "q60",
                "text": "¿Cuál es la principal barrera que enfrenta su organización para avanzar en sostenibilidad, y qué apoyo requeriría de sus clientes/compradores para superarla?",
                "type": "open",
                "placeholder": "Describa libremente la situación..."
            },
        ]
    },
]


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
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=ACCENT,
        alignment=TA_CENTER,
        spaceAfter=2
    )
    section_title_style = ParagraphStyle(
        'SectionTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.white,
        spaceAfter=2
    )
    section_sub_style = ParagraphStyle(
        'SectionSub', parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=ACCENT,
        spaceAfter=0
    )
    question_style = ParagraphStyle(
        'Question', parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=TEXT_DARK,
        spaceBefore=6,
        spaceAfter=3
    )
    answer_style = ParagraphStyle(
        'Answer', parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_GRAY,
        leftIndent=10,
        spaceAfter=4
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_DARK,
        spaceAfter=3
    )

    elements = []

    # Header block
    header_data = [[
        Paragraph("DIAGNÓSTICO DE SOSTENIBILIDAD PARA PROVEEDORES", title_style),
    ]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), MILITARY_GREEN),
        ('ROWPADDING', (0,0), (-1,-1), 16),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(header_table)

    sub_data = [[Paragraph("60 preguntas estructuradas | GRI · ISO 20400 · UNGPs · TCFD · ESRS · ISO 45001 · ISO 14001", subtitle_style)]]
    sub_table = Table(sub_data, colWidths=[17*cm])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_GREEN),
        ('ROWPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 0.5*cm))

    # Meta info
    meta_data = [
        [Paragraph(f"<b>Empresa:</b> {company_name}", meta_style),
         Paragraph(f"<b>Contacto:</b> {contact_name}", meta_style)],
        [Paragraph(f"<b>Email:</b> {contact_email}", meta_style),
         Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", meta_style)],
    ]
    meta_table = Table(meta_data, colWidths=[8.5*cm, 8.5*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('ROWPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,-1), (-1,-1), 1, LIGHT_GREEN),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.5*cm))

    # Sections
    for section in SECTIONS:
        sec_header = [[
            Paragraph(f"{section['id']}. {section['title']}", section_title_style),
            Paragraph(section['subtitle'], section_sub_style)
        ]]
        sec_table = Table(sec_header, colWidths=[17*cm])
        sec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), MILITARY_GREEN),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 2),
            ('TOPPADDING', (0,1), (-1,1), 0),
            ('BOTTOMPADDING', (0,1), (-1,1), 8),
        ]))
        elements.append(sec_table)

        for q in section['questions']:
            elements.append(Paragraph(f"• {q['text']}", question_style))
            answer = form_data.get(q['id'], "—")
            if not answer:
                answer = "Sin respuesta"
            elements.append(Paragraph(f"Respuesta: {answer}", answer_style))

        elements.append(Spacer(1, 0.3*cm))

    # Footer
    footer_data = [[
        Paragraph("Diagnóstico gestionado a través de la plataforma <b>GALILEO</b> · Tratamiento confidencial exclusivo para evaluación ESG", 
                  ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.white, alignment=TA_CENTER))
    ]]
    footer_table = Table(footer_data, colWidths=[17*cm])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_GREEN),
        ('ROWPADDING', (0,0), (-1,-1), 10),
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
    msg['Subject'] = f"Diagnóstico ESG GALILEO – {company_name}"

    body = f"""Se ha recibido un nuevo Diagnóstico de Sostenibilidad ESG a través de la plataforma GALILEO.

Empresa: {company_name}
Contacto: {contact_email}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Adjunto encontrará el informe completo en formato PDF.

—
Plataforma GALILEO | Diagnóstico ESG para Proveedores
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    filename = f"diagnostico_esg_{company_name.replace(' ', '_')}.pdf"
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())


@app.route('/')
def index():
    return render_template('index.html', sections=SECTIONS)


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    company_name = data.get('company_name', 'Empresa')
    contact_name = data.get('contact_name', '')
    contact_email = data.get('contact_email', '')
    answers = data.get('answers', {})

    try:
        pdf_bytes = generate_pdf(answers, company_name, contact_name, contact_email)
        send_email(pdf_bytes, company_name, contact_email)
        return jsonify({'success': True, 'message': 'Diagnóstico enviado correctamente.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
