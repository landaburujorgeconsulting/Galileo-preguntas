# GALILEO – Diagnóstico ESG para Proveedores

Aplicación web Flask para el diagnóstico de sostenibilidad de proveedores con 60 preguntas en 14 secciones ESG. Al completar el formulario, se genera un PDF y se envía automáticamente por email.

---

## Estructura del proyecto

```
galileo_app/
├── app.py              # Aplicación principal Flask
├── requirements.txt    # Dependencias Python
├── render.yaml         # Configuración para Render
├── README.md
└── templates/
    └── index.html      # Template HTML (Jinja2)
```

---

## Configuración del email (Gmail)

Para que el envío de PDF funcione, necesitás configurar dos variables de entorno:

| Variable    | Descripción                                |
|-------------|--------------------------------------------|
| `MAIL_USER` | Tu dirección Gmail (ej: tumail@gmail.com)  |
| `MAIL_PASS` | **App Password** de Google (ver abajo)     |

### Cómo obtener un App Password de Gmail:
1. Andá a [myaccount.google.com/security](https://myaccount.google.com/security)
2. Activá la **Verificación en dos pasos** si no la tenés
3. Buscá **"Contraseñas de aplicaciones"** y generá una nueva
4. Usá esa contraseña de 16 caracteres como `MAIL_PASS`

---

## Deploy en Render

### Paso 1 – Subir a GitHub
```bash
git init
git add .
git commit -m "GALILEO ESG app inicial"
git remote add origin https://github.com/TU_USUARIO/galileo-esg.git
git push -u origin main
```

### Paso 2 – Crear servicio en Render
1. Entrá a [render.com](https://render.com) y hacé clic en **"New → Web Service"**
2. Conectá tu repositorio de GitHub
3. Configurá:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. En **Environment Variables**, agregá:
   - `MAIL_USER` → tu cuenta de Gmail
   - `MAIL_PASS` → tu App Password

### Paso 3 – Deploy
Render desplegará automáticamente. La URL pública quedará disponible en el dashboard.

---

## Ejecución local (desarrollo)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export MAIL_USER="tumail@gmail.com"
export MAIL_PASS="tu_app_password"

# Iniciar servidor
python app.py
```

Abrí el navegador en: `http://localhost:5000`

---

## Funcionamiento

1. El usuario completa datos de empresa y contacto
2. Navega por las 14 secciones ESG (tipo pestañas/hojas)
3. Responde las 60 preguntas con opciones o texto libre
4. Al finalizar, hace clic en "Enviar Diagnóstico"
5. El servidor genera el PDF con ReportLab y lo envía por email a **nodoconsultoria2015@gmail.com**

---

## Marcos normativos cubiertos
GRI 2021 · ISO 20400:2017 · UNGPs · TCFD/TNFD · ESRS/CSRD · ISO 45001 · ISO 14001 · OIT
