from flask import Flask, g
from .app_factory import create_app
from .db_connect import close_db, get_db
from app.functions import load_user

app = create_app()
app.secret_key = 'your-secret'  # Replace with an environment variable

# Register Blueprints
from app.blueprints.auth import auth
from app.blueprints.users import users
from app.blueprints.brother_catalog import brother_catalog
from app.blueprints.slags import slags
from app.blueprints.admin import admin

app.register_blueprint(auth)
app.register_blueprint(users)
app.register_blueprint(brother_catalog)
app.register_blueprint(slags)
app.register_blueprint(admin)

from . import routes

@app.before_request
def before_request():
    g.db = get_db()

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.context_processor
def inject_user():
    load_user()
    return dict(user=g.user)