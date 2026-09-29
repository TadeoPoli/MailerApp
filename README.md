# ✉️ MailerApp

**MailerApp** es una aplicación web educativa desarrollada con **Python, Flask y MySQL** para registrar, consultar y buscar correos enviados. Incluye una integración opcional con SendGrid para el envío de mensajes cuando el entorno dispone de las credenciales necesarias.

> **Nota:** Este proyecto tiene fines educativos y de práctica Full-Stack. No representa un servicio comercial de correo ni debe considerarse una aplicación lista para desplegar públicamente sin medidas adicionales.

## 📸 Vistas principales

### Historial y búsqueda

La vista principal muestra los correos registrados en MySQL e incluye una búsqueda sobre el contenido almacenado.

![Listado y búsqueda de correos](<screenshots/Captura de pantalla 2026-09-29 151155.png>)

### Formulario de envío

El formulario valida destinatario, asunto y contenido antes de intentar el envío. Si SendGrid no está configurado, muestra un mensaje controlado y el resto de la aplicación continúa disponible.

![Formulario de envío de correo](<screenshots/Captura de pantalla 2026-09-29 151208.png>)

## ✨ Funcionalidades

- Historial de correos enviados y registrados en MySQL.
- Búsqueda sobre el contenido de los correos almacenados.
- Formulario de envío con validación de destinatario, asunto y contenido.
- Integración con SendGrid cuando el entorno está configurado.
- Persistencia del registro del correo después de que SendGrid acepta el envío.
- Mensaje controlado cuando SendGrid no está configurado.

## 🧰 Tecnologías utilizadas

- **Python 3**
- **Flask**
- **MySQL** mediante `mysql-connector-python`
- **SendGrid** mediante su SDK oficial
- **python-dotenv** para configuración local
- **HTML5**, plantillas Jinja y **CSS** propio
- **Gunicorn** para el comando de servidor definido en `Procfile`

## ⚙️ Requisitos

- Python 3 y `pip`.
- MySQL en ejecución con un usuario local que pueda utilizar una base de datos.
- PowerShell en Windows.
- Una cuenta de SendGrid solo si se desea habilitar el envío real de correos.

## 🚀 Instalación local

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

También se puede usar el intérprete del entorno virtual sin activarlo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 🔐 Configuración mediante `.env`

Completá el archivo `.env` local creado a partir de `.env.example`. Este archivo está excluido de Git y no debe publicarse.

```text
SECRET_KEY=
FLASK_DATABASE_HOST=127.0.0.1
FLASK_DATABASE_PORT=3306
FLASK_DATABASE_USER=
FLASK_DATABASE_PASSWORD=
FLASK_DATABASE=
SENDGRID_API_KEY=
FROM_EMAIL=
```

No incluyas credenciales reales en archivos versionados.

## 🗄️ Configuración de MySQL

Creá una base de datos local cuyo nombre coincida con `FLASK_DATABASE`:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u TU_USUARIO -p -h 127.0.0.1 -P 3306 -e "CREATE DATABASE IF NOT EXISTS mailer_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Luego inicializá las tablas:

```powershell
python -m flask --app app init-db
```

La inicialización actual utiliza `CREATE TABLE IF NOT EXISTS`; crea la tabla requerida cuando no existe y no está diseñada para borrar registros existentes.

## ▶️ Ejecución local

```powershell
python -m flask --app app run --debug
```

Abrí [http://127.0.0.1:5000/](http://127.0.0.1:5000/) en el navegador.

## 📬 SendGrid opcional

SendGrid no es necesario para iniciar la aplicación, consultar el historial, usar la búsqueda ni inicializar MySQL. Para habilitar el envío, configurá estas variables en `.env`:

```text
SENDGRID_API_KEY=
FROM_EMAIL=
```

- `SENDGRID_API_KEY` debe contener una API Key válida proporcionada por SendGrid.
- `FROM_EMAIL` debe ser un remitente autorizado o verificado en SendGrid.
- Ninguno de estos valores debe publicarse.

La integración está preparada en el código, pero no se realizó un envío real durante las pruebas actuales porque no se configuraron credenciales reales de SendGrid. Sin esta configuración, el intento de envío muestra el mensaje: **“El envío de correos no está configurado en este entorno.”**

## 🛡️ Buenas prácticas de seguridad incorporadas

| Riesgo abordado | Medida incorporada |
| --- | --- |
| Configuración sensible | Variables de entorno y `.env` excluido de Git. |
| Inyección SQL | Consultas parametrizadas mediante `mysql-connector-python`. |
| CSRF | Token asociado a la sesión y validado en solicitudes `POST`. |
| Datos inválidos | Validación de email, asunto, contenido y longitudes. |
| Sesiones | Cookies `HttpOnly` y `SameSite=Lax`. |
| Errores externos | Mensajes controlados sin exponer detalles internos de MySQL o SendGrid. |

Estas medidas son buenas prácticas incorporadas al proyecto educativo, pero no sustituyen una revisión de seguridad y operaciones para producción.

## Limitaciones

- No se realizó una prueba de envío real mediante SendGrid.
- La aplicación no cuenta con autenticación ni mecanismos antiabuso suficientes para exponer públicamente el formulario de envío y el historial de correos.
- Antes de un despliegue público deberían considerarse autenticación, rate limiting, controles antiabuso y una revisión de privacidad de los datos almacenados.

## ✅ Estado actual

Se comprobó localmente el inicio con Flask, la inicialización de MySQL, el listado, la búsqueda, el formulario y las validaciones. La ausencia de configuración de SendGrid se maneja de forma controlada; el envío real queda pendiente de una cuenta y remitente verificados.
