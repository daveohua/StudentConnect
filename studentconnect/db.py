import sqlite3
import csv

import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(*args):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as current_file:
        db.executescript(current_file.read().decode('utf8'))

    with current_app.open_resource('static/subject.csv', 'rt') as current_file:
        db.executemany("INSERT INTO Subject (Name, Level, Qualification) VALUES (?, ?, ?)",
                       csv.reader(current_file))
        db.commit()


@click.command('init-db')
def init_db_command():
    """clear existing data and create new tables"""
    init_db()
    click.echo('Initialised the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
