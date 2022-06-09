from flask import Blueprint, request, redirect, url_for
from flask.helpers import flash
from flask.json import jsonify
from flask.templating import render_template
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from .libs import *
from . import Message, mail_address, mail, error_msg
from cryptography.fernet import Fernet, InvalidToken
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username').lower()
        password = request.form.get('password')
        remember = request.form.get('remember')
        remember = True if remember else False
        user = User.query.filter_by(username=username).first()
        if user:
            if hash_password(password, user.salt) == user.password:
                flash('Successfully logged in!', category='success')
                login_user(user, remember=remember)
                return redirect(url_for("views.home"))
            else:
                flash('Incorrect username or password', category='danger')
        else:
            flash('Incorrect username or password', category='danger')
    return render_template('login.html', user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('user_name')
        password = request.form.get('password')
        remember = request.form.get('remember')
        remember = True if remember else False
        user = User.query.filter_by(username=username).first()
        error = False
        if user:
            flash("Username already exists", category='danger')
            error = True
        if len(username) < 4:
            flash("Username is too short", category='danger')
            error = True
        if len(password) < 7:
            flash("Password is too short", category='danger')
            error = True
        if not error:
            salt = gen_salt()
            new_user = User(email=email, 
                        username=username,
                        salt=salt, password=hash_password(password, salt))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=remember)
            return redirect(url_for('views.home'))
    return render_template('sign-up.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
