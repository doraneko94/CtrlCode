from app import db
from datetime import datetime
from flask_login import UserMixin
from .consts import INITIAL_RATING

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Float, default=INITIAL_RATING)  # 初期レート
    is_confirmed = db.Column(db.Boolean, default=False)
    code_is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())