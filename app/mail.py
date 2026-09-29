import re

import sendgrid
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import Email, Mail, To

from app.db import get_db

bp = Blueprint('mail', __name__, url_prefix='/')
MAX_SEARCH_LENGTH = 100
MAX_SUBJECT_LENGTH = 200
MAX_CONTENT_LENGTH = 5000
EMAIL_PATTERN = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


class SendGridNotConfiguredError(RuntimeError):
    """Señala que el envío no fue habilitado en la configuración local."""


def validate_email_address(email):
    return bool(email and len(email) <= 254 and EMAIL_PATTERN.fullmatch(email))


def validate_message(email, subject, content):
    errors = []
    if not validate_email_address(email):
        errors.append('Ingresá una dirección de correo válida.')
    if not subject:
        errors.append('El asunto es obligatorio.')
    elif len(subject) > MAX_SUBJECT_LENGTH:
        errors.append(f'El asunto no puede superar los {MAX_SUBJECT_LENGTH} caracteres.')
    if not content:
        errors.append('El contenido es obligatorio.')
    elif len(content) > MAX_CONTENT_LENGTH:
        errors.append(f'El contenido no puede superar los {MAX_CONTENT_LENGTH} caracteres.')
    return errors

@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search', '').strip()
    if len(search) > MAX_SEARCH_LENGTH:
        flash(f'La búsqueda no puede superar los {MAX_SEARCH_LENGTH} caracteres.')
        search = search[:MAX_SEARCH_LENGTH]

    db, c = get_db()
    if not search:
        c.execute('SELECT id, email, subject, content FROM email ORDER BY id DESC')
    else:
        c.execute(
            'SELECT id, email, subject, content FROM email WHERE content LIKE %s ORDER BY id DESC',
            ('%' + search + '%',),
        )

    mails = c.fetchall()
    return render_template('mails/index.html', mails=mails, search=search)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        content = request.form.get('content', '').strip()
        errors = validate_message(email, subject, content)

        if not errors:
            try:
                send_email(email, subject, content)
            except SendGridNotConfiguredError:
                flash('El envío de correos no está configurado en este entorno.')
                return render_template('mails/create.html', email=email, subject=subject, content=content)
            except HTTPError:
                current_app.logger.exception('SendGrid rechazó el envío de correo.')
                flash('No se pudo enviar el correo. Revisá la configuración e intentá nuevamente.')
                return render_template('mails/create.html', email=email, subject=subject, content=content)
            except Exception:
                current_app.logger.exception('Error inesperado durante el envío de correo.')
                flash('No se pudo enviar el correo en este momento. Intentá nuevamente.')
                return render_template('mails/create.html', email=email, subject=subject, content=content)

            db = None
            try:
                db, c = get_db()
                c.execute(
                    'INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)',
                    (email, subject, content),
                )
                db.commit()
            except Exception:
                if db is not None:
                    db.rollback()
                current_app.logger.exception('El correo se envió, pero no pudo registrarse en MySQL.')
                flash('El correo fue aceptado para envío, pero no pudo registrarse localmente.')
                return render_template('mails/create.html', email=email, subject=subject, content=content)

            flash('Correo enviado y registrado correctamente.')
            return redirect(url_for('mail.index'))

        for error in errors:
            flash(error)

    return render_template(
        'mails/create.html',
        email=request.form.get('email', ''),
        subject=request.form.get('subject', ''),
        content=request.form.get('content', ''),
    )


def send_email(to, subject, content):
    """Envía texto plano y comprueba que SendGrid acepte el mensaje."""
    api_key = current_app.config.get('SENDGRID_KEY')
    from_email = current_app.config.get('FROM_EMAIL')
    if not api_key or not validate_email_address(from_email):
        raise SendGridNotConfiguredError()

    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to),
        subject=subject,
        plain_text_content=content,
    )
    client = sendgrid.SendGridAPIClient(api_key=api_key)
    response = client.send(message)

    if not 200 <= response.status_code < 300:
        raise RuntimeError(f'SendGrid devolvió el estado {response.status_code}.')
