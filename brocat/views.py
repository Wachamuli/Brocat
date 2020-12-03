import os

from flask import render_template, redirect, url_for, \
    flash, session, request
from flask_login import login_user, login_required, logout_user, \
    current_user
from urllib.parse import urlparse, urljoin

from brocat import app, login_manager
from brocat.database import db_session
from brocat.models import Users
from brocat.forms import CreateAccountForm, LoginForm, UploadBrocatForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    ca_form = CreateAccountForm()
    if ca_form.validate_on_submit():
        new_user = Users(
            ca_form.email.data, 
            ca_form.username.data, 
            ca_form.password.data
        )

        try:
            db_session.add(new_user)
            db_session.commit()
            return redirect(url_for('login'))
        except:
            db_session.rollback()
            return 'Error in the db'

    return render_template('create_account.html', form=ca_form)


# def is_safe_url(target):
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#         ref_url.netloc == test_url.netloc


@app.route('/login', methods=['GET', 'POST'])
def login():
    log_form = LoginForm()
    # session['next'] = request.args.get('next')

    if log_form.validate_on_submit():
        username = log_form.username.data
        psw = log_form.password.data
        remember = log_form.remember.data

        user_exists = Users.query.filter_by(username=username).first()
        if user_exists and user_exists.check_psw(psw):
            login_user(user_exists, remember=remember)
            flash('Logged succesfully.')
            # if 'next' in session:
            #     next = session['next']
            #     if is_safe_url(next):
            #         return redirect(next)

            return redirect('/')

        return 'Invalid username or password.'

    return render_template('login.html', form=log_form)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    flash('Logout successfully')
    logout_user()
    return redirect('/login')


@app.route('/home')
@login_required
def my_profile():
    return f'<h1>This is your profile, {current_user}</h1>'


def validate_format(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/home/upload_podcast', methods=['GET', 'POST'])
@login_required
def upload_podcast():
    img_folder = app.config['IMAGES_FOLDER']
    img_extensions = app.config['ALLOWED_IMAGES_EXTENSIONS']
    aud_folder = app.config['AUDIOS_FOLDER']
    aud_extensions = app.config['ALLOWED_AUDIOS_EXTENSIONS']

    form = UploadBrocatForm()

    # if form.validate_on_submit():

    return 'This is the upload page'


# @login_manager.unauthorized_handler
# def unauthorized():
#     pass


# @app.errorhandler(404)
# def error():
#     pass
