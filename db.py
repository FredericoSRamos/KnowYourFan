from flask import current_app, g
from flask_dance.contrib.twitch import make_twitch_blueprint
import click
import sqlite3

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource("./instance/schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))

@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Database initialized.")

def init_app(app):
    app.config.from_pyfile("config.py")
    
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    twitch_bp = make_twitch_blueprint()
    app.register_blueprint(twitch_bp, url_prefix='/twitch_login')