import os

from flask import render_template, redirect, url_for, \
    flash, Blueprint, current_app as app
from flask_login import login_user, logout_user, login_required, \
    current_user
from werkzeug.utils import secure_filename

from brocat.database import db_session
from brocat.models import Users, Brocat
from brocat.forms import CreateAccountForm, LoginForm, UploadBrocatForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


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
            return redirect(url_for('login'))
        except:
            db_session.rollback()
            return 'Error in the db'

    return render_template('create_account.html', form=ca_form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    log_form = LoginForm()

    if log_form.validate_on_submit():
        user = log_form.check_user.data
        remember = log_form.remember.data

        login_user(user, remember=remember)
        flash('Logged succesfully.')
        return redirect('/')

    return render_template('login.html', form=log_form,)



@main.route('/logout')
@login_required
def logout():
    flash('Logout successfully')
    logout_user()
    return redirect('/login')


@main.route('/home')
@login_required
def home():
    return f'<h1>This is your profile, {current_user}</h1>'


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

        there_thumb = not '' in str(thumbnail)
        if there_thumb:
            thumbnail_filename = secure_filename(thumbnail.filename)
            thumb_path = os.path.join(img_folder, thumbnail_filename)
            thumbnail.save(thumb_path)
        else:
            thumb_path = None

        audio_filename = secure_filename(audio.filename)
        aud_path = os.path.join(aud_folder, audio_filename)
        audio.save(aud_path)

        new_brocat = Brocat(
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
