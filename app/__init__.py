from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import os, sys

app = Flask(__name__)
for env in ["SECRET_KEY", "MAIL_PASSWORD", "MAIL_USERNAME", "MAIL_SERVER"]:
    app.config[env] = os.getenv(env)
    if app.config[env] is None:
        print(f"Env {env} is None.")
        sys.exit()
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

is_tls = os.getenv("MAIL_USE_TLS")
if is_tls is None:
    print("Env MAIL_USE_TLS is None.")
    sys.exit()
else:
    if is_tls == "True":
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        app.config["MAIL_USE_SSL"] = False
    else:
        app.config["MAIL_PORT"] = 465
        app.config["MAIL_USE_TLS"] = False
        app.config["MAIL_USE_SSL"] = True

app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{os.path.join(os.getcwd(), "database.db")}'

mail = Mail(app)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CSRFProtect(app)

from app.routes import *

app.register_blueprint(main)
app.register_blueprint(home_bp)
app.register_blueprint(register_bp)