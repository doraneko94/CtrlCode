from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from app import app
from app.models import User
from routes import main, home_bp

login_bp = Blueprint("login", __name__)
limiter = Limiter(get_remote_address, app=app)

@login_bp.route("/login")
def login():
    return render_template("login.html")

@login_bp.route("/login-submit", methods=["POST"])
@limiter.limit("5 per minute")
def login_submit():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        if not user.is_confirmed:
            flash('ログインする前に、メールアドレスを確認してください', 'error')
            return redirect(url_for('login.login'))
        else:
            login_user(user)
            return redirect(url_for("home_bp.home"))
    else:
        flash("ユーザ名またはパスワードが違います")
        return redirect(url_for("login.login"))
    
@login_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return render_template("message.html", title="ログアウト完了", heading="ログアウトしました", message="再度ログインしてください")