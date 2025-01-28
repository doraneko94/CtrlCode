import os, shutil
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_mail import Message
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from app import db, mail
from app.models import User
from app.utils import confirm_token, generate_confirmation_token
from routes import main

register_bp = Blueprint("register", __name__)

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(message="ユーザ名は必須です"),
        Regexp(r"^[a-zA-Z0-9]+$", message="ユーザ名にはアルファベットの大文字・小文字と数字のみ使用できます（半角）"),
        Length(min=4, max=20, message="ユーザ名は4文字以上16文字以内です")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="パスワードは必須です"),
        Regexp(
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[A-Za-z0-9!@#$%^&+=]{8,}$',
            message="パスワードにはアルファベットの大文字・小文字、数字、記号（!@#$%^&+=）のみ使用できます（半角）。アルファベット大文字・小文字・数字は、それぞれ最低1文字以上含めてください"
        ),
        Length(min=8, max=32, message="パスワードは8文字以上32文字以下です")
    ])
    confirm_password = PasswordField("Confirm PAssword", validators=[
        DataRequired(message="パスワードをもう一度入力してください"),
        EqualTo("password", message="パスワードが一致しません")
    ])
    email = EmailField("Email", validators=[
        DataRequired(message="メールアドレスは必須です"),
        Email(message="入力されたメールアドレスは使用できません")
    ])
    confirm_email = EmailField("Confirm Email", validators=[
        DataRequired(message="メールアドレスをもう一度入力してください"),
        EqualTo("email", message="メールアドレスが一致しません")
    ])
    submit = SubmitField("Register")

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data

        is_available, message = email_is_available(email)
        if not is_available:
            flash(message)
            return redirect(url_for("register_bp.register"))
        
        is_available, message = username_is_available(username)
        if not is_available:
            flash(message)
            return redirect(url_for("register_bp.register"))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        token = generate_confirmation_token(email)
        confirm_url = url_for("register_bp.confirm_email", token=token, _external=True)
        html = render_template("email_confirmation.html", username=username, confirm_url=confirm_url)

        msg = Message("メールアドレスを確認してください", recipients=[email], html=html)
        mail.send(msg)

        user_folder = os.path.join("user_files", username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            default_file = os.path.join("app", "default.py")
            user_file = os.path.join(user_folder, "module.py")
            shutil.copy(default_file, user_file)

        return render_template(
            "message.html",
            title="確認メール送信",
            heading="メールアドレス確認用のリンクを送りました",
            message=f"{email}宛に確認メールを送りました。メール内のリンクをクリックして、アカウントを有効化してください"
        )
    return render_template("register.html", form=form)

def username_is_available(username):
    if User.query.filter_by(username=username).first():
        return False, "このユーザ名は既に使用されています"
    else:
        return True, None
    
def email_is_available(email):
    if User.query.filter_by(email=email).first():
        return False, "このメールアドレスは既に登録されています"
    else:
        return True, None

@register_bp.route("/check_availability")
def check_availability():
    data = request.json
    field = data.get("field")
    value = data.get("value")

    if field == "username":
        is_available, message = username_is_available(value)
        return jsonify({"available": is_available, "message": message})
    elif field == "email":
        is_available, message = email_is_available(value)
        return jsonify({"available": is_available, "message": message})
    return jsonify({"available": True})

@register_bp.route("/confirm/<token>")
def confirm_email(token):
    title = "メールアドレス確認"
    heading = "メールアドレスを確認しました"
    message = "ログインページからログインしてください"
    try:
        email = confirm_token(token)
    except:
        title = "メールアドレス確認失敗"
        heading = "メールアドレスの確認に失敗しました"
        message = "確認リンクが不正、または有効期限が切れています"
        return render_template("message.html", title=title, heading=heading, message=message)
    
    user = User.query.filter_by(email=email).first_or_404()

    if user.is_confirmed:
        heading = "メールアドレスは既に確認済みです"
    else:
        user.is_confirmed = True
        db.session.commit()
    return render_template("message.html", title=title, heading=heading, message=message)