import sqlite3
from . import app
import click
from flask import g
from flask.cli import with_appcontext


def getDataBase():
    if "database" not in g:
        g.database = sqlite3.connect(
            app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.database.row_factory = sqlite3.Row
    return g.database


def closeDataBase(e=None):
    database = g.pop('database', None)
    if database is not None:
        database.close()


def initDataBase():
    database = getDataBase()
    with app.open_resource('schema.sql') as f:
        database.executescript(f.read().decode('utf8'))


@click.command('init-database')
@with_appcontext
def initDataBaseCommand():
    initDataBase()
    click.echo("Initialized the database!!")

def initApp():
    app.teardown_appcontext(closeDataBase)
    app.cli.add_command(initDataBaseCommand)