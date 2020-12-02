import os

from flask import render_template, redirect, url_for, \
    flash
from flask_login import login_user, login_required, logout_user, \
    current_user, AnonymousUserMixin

from brocat import app, login_manager
from brocat.database import db_session
from brocat.models import Users
from brocat.forms import CreateAccountForm, LoginForm, UploadBrocatForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        email = form.email.data
        user = form.username.data
        psw = form.password.data

        if Users.query.filter_by(username=user).first():
            return 'This user already exists'
        if Users.query.filter_by(e_mail=email).first():
            return 'This email already exsts'

        new_user = Users(email, user, psw)

        try:
            db_session.add(new_user)
            db_session.commit()
            flash('Account created, now login')
            return redirect(url_for('login'))
        except:
            db_session.rollback()
            return 'Error in the db'

    return render_template('create_account.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        psw = form.password.data
        user_exists = Users.query.filter_by(username=username).first()

        if user_exists and user_exists.check_psw(psw):
            login_user(user_exists)
            url_for('my_profile', username=username)
            return redirect('/')
        else:
            return 'Invalid username or password.'

    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successfully')
    return redirect('/')


@app.route('/<username>')
@login_required
def my_profile(username):
    return f'This is your profile, {username}'


def validate_format(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/<username>/upload_podcast', methods=['GET', 'POST'])
@login_required
def upload_podcast(username):
    img_folder = app.config['IMAGES_FOLDER']
    img_extensions = app.config['ALLOWED_IMAGES_EXTENSIONS']
    aud_folder = app.config['AUDIOS_FOLDER']
    aud_extensions = app.config['ALLOWED_AUDIOS_EXTENSIONS']

    form = UploadBrocatForm()

    # if form.validate_on_submit():

    return 'This is the upload page'
