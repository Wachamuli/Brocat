import os
import random

from flask import render_template, redirect, flash, request, \
    Blueprint, abort, current_app as app
from flask_login import login_user, logout_user, login_required, \
    current_user
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin

from brocat.database import db_session
from brocat.models import Users, Brocats
from brocat.forms import CreateAccountForm, LoginForm, UploadBrocatForm

main = Blueprint('main', __name__)


@main.route('/')
def index():
    total_brocats = Brocats.query.count()
    encontered_list = []
    for _ in range(0, 20):
        rand = random.randint(0, total_brocats)
        brocat = Brocats.query.filter_by(id=rand).first()
        encontered_list.append(brocat)
    
    return render_template('index.html', brocats_list=encontered_list)


@main.route('/create_account', methods=['GET', 'POST'])
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
            return redirect('/login')
        except:
            db_session.rollback()
            return 'Error in the db'

    return render_template('create_account.html', form=ca_form)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@main.route('/login', methods=['GET', 'POST'])
def login():
    log_form = LoginForm()
    if log_form.validate_on_submit():
        user = log_form.check_user.data
        remember = log_form.remember.data
        
        login_user(user, remember=remember)
        flash('Logged succesfully.')
        next = request.args.get('next')
        
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or '/')

    return render_template('login.html', form=log_form,)


@main.route('/logout')
def logout():
    logout_user()
    if current_user.is_authenticated:
        flash('Logout successfully')
    return redirect('/login')


@main.route('/home')
@login_required
def home():
    user_brocats = []
    for brocat in current_user.brocats:
        user_brocats.append(brocat.title)
        
    return render_template('home.html', user=current_user, user_brocats=user_brocats)


@main.route('/home/upload_brocat', methods=['GET', 'POST'])
@login_required
def upload_brocat():
    img_folder = app.config['IMAGES_FOLDER']
    aud_folder = app.config['AUDIOS_FOLDER']

    upload_form = UploadBrocatForm()
    if upload_form.validate_on_submit():
        title = upload_form.title.data
        thumbnail = upload_form.thumbnail.data
        audio = upload_form.audio.data
        description = upload_form.description.data

        thumbnail_filename = secure_filename(thumbnail.filename)
        audio_filename = secure_filename(audio.filename)
        thumb_path = os.path.join(img_folder, thumbnail_filename)
        aud_path = os.path.join(aud_folder, audio_filename)
        thumbnail.save(thumb_path)
        audio.save(aud_path)

        new_brocat = Brocats(
            title,
            thumb_path,
            aud_path,
            description
        )

        try:
            db_session.add(new_brocat)
            db_session.commit()
            return 'Uploaded'
        except:
            db_session.rollback()
            return 'Error in the db'

    return render_template('upload_brocat.html', form=upload_form)


# @login_manager.unauthorized_handler
# def unauthorized():
#     pass


# @main.errorhandler(404)
# def error():
#     pass
