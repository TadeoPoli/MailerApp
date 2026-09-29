import mysql.connector

import click
from flask import current_app, g
from flask.cli import with_appcontext
from .schema import instructions

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            port=current_app.config['DATABASE_PORT'],
            host=current_app.config['DATABASE_HOST'],
            user=current_app.config['DATABASE_USER'],
            password=current_app.config['DATABASE_PASSWORD'],
            database=current_app.config['DATABASE'],
        )
    cursor = g.db.cursor(dictionary=True)
    return g.db, cursor

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db, c = get_db()

    try:
        for instruction in instructions:
            c.execute(instruction)
        db.commit()
    finally:
        c.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Tabla de correos verificada o creada sin eliminar datos existentes.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
    
