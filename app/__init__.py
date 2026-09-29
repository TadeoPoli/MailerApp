import os

from dotenv import load_dotenv
from flask import Flask, request


def _load_configuration(app):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(project_root, '.env'))

    required_values = {
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'FLASK_DATABASE_USER': os.environ.get('FLASK_DATABASE_USER'),
        'FLASK_DATABASE_PASSWORD': os.environ.get('FLASK_DATABASE_PASSWORD'),
        'FLASK_DATABASE': os.environ.get('FLASK_DATABASE'),
    }
    missing = [name for name, value in required_values.items() if not value]
    if missing:
        raise RuntimeError('Faltan variables de entorno requeridas: ' + ', '.join(missing))

    try:
        database_port = int(os.environ.get('FLASK_DATABASE_PORT', '3306'))
    except ValueError as error:
        raise RuntimeError('FLASK_DATABASE_PORT debe ser un número válido.') from error

    app.config.from_mapping(
        SECRET_KEY=required_values['SECRET_KEY'],
        DATABASE_HOST=os.environ.get('FLASK_DATABASE_HOST', '127.0.0.1'),
        DATABASE_PORT=database_port,
        DATABASE_USER=required_values['FLASK_DATABASE_USER'],
        DATABASE_PASSWORD=required_values['FLASK_DATABASE_PASSWORD'],
        DATABASE=required_values['FLASK_DATABASE'],
        # SendGrid es opcional para consultar la aplicación e inicializar MySQL.
        # Se valida al intentar enviar un correo.
        SENDGRID_KEY=os.environ.get('SENDGRID_API_KEY'),
        FROM_EMAIL=os.environ.get('FROM_EMAIL'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        _load_configuration(app)
    else:
        app.config.from_mapping(test_config)

    from . import db
    from .csrf import csrf_token, validate_csrf_token

    db.init_app(app)

    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': csrf_token}

    @app.before_request
    def protect_post_requests():
        if request.method == 'POST':
            validate_csrf_token()

    @app.errorhandler(400)
    def bad_request(error):
        return (
            'La solicitud no es válida o su sesión expiró. Volvé a cargar la página e intentá nuevamente.',
            400,
        )

    from . import mail

    app.register_blueprint(mail.bp)
    return app
