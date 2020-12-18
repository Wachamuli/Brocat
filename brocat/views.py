import os
import random

from flask import render_template, redirect, flash, request, \
    Blueprint, abort, current_app as app, send_from_directory, \
        jsonify
from flask_login import login_user, logout_user, login_required, \
    current_user
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin
from jinja2 import TemplateNotFound

from brocat.database import db_session
from brocat.models import Users, Brocats, users_schema, brocats_schema, \
    user_schema, brocat_schema
from brocat.forms import CreateAccountForm, LoginForm, UploadBrocatForm

main = Blueprint('main', __name__)


def _render_template(template, **context):
    try:
        return render_template(template, **context)
    except TemplateNotFound:
        abort(404)


@main.route('/')
def index():
    total_brocats = Brocats.query.count()
    encontered_list = []
    for _ in range(0, total_brocats):
        rand = random.randint(2, total_brocats)
        brocat = Brocats.query.filter_by(id=rand).first()
        encontered_list.append(brocat)

    return _render_template('index.html', brocats_list=encontered_list)


@main.route('/watch=<int:brocat_id>')
def watch(brocat_id):
    brocat = Brocats.query.get(brocat_id)
    if brocat:
        return _render_template('watch.html', brocat=brocat)

    return 'No available'


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

    return _render_template('create_account.html', form=ca_form)


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

    return _render_template('login.html', form=log_form)


@main.route('/logout')
def logout():
    if current_user.is_authenticated:
        flash('Logout successfully')

    logout_user()
    return redirect('/login')


@main.route('/home')
@login_required
def home():
    user_brocats = []
    for brocat in current_user.brocats:
        user_brocats.append(brocat.title)

    return _render_template('home.html', user=current_user, user_brocats=user_brocats)


@main.route('/home/upload_brocat', methods=['GET', 'POST'])
@login_required
def upload_brocat():
    upload_form = UploadBrocatForm()
    if upload_form.validate_on_submit():
        img_folder = app.config['IMAGES_FOLDER']
        aud_folder = app.config['AUDIOS_FOLDER']

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
            thumbnail_filename,
            audio_filename,
            description
        )

        try:
            db_session.add(new_brocat)
            db_session.commit()
            flash('Uploaded Brocat')
            return redirect('/')
        except:
            db_session.rollback()
            return 'Error in the db'

    return _render_template('upload_brocat.html', form=upload_form)


@main.route('/get_aud/<audname>')
def get_aud(audname):
    return send_from_directory(app.config['AUDIOS_FOLDER'], filename=audname)


@main.route('/get_img/<imgname>')
def get_img(imgname):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename=imgname)


@main.route('/api/users')
def all_users():
    all_users = Users.query.all()
    response = users_schema.dump(all_users)
    return jsonify(response)


@main.route('/api/users/<int:id>')
def get_user(id):
    user = Users.query.get(id)
    response = user_schema.dump(user)
    if len(response) == 0:
        response = 'User not found!'

    return response


@main.route('/api/brocats')
def all_brocats():
    all_brocats = Brocats.query.all()
    response = brocats_schema.dump(all_brocats)
    return jsonify(response)

@main.route('/api/brocats/<int:id>')
def get_brocat(id):
    brocat = Brocats.query.get(id)
    response = brocat_schema.dump(brocat)
    if len(response) == 0:
        response = 'Brocat not found!'
    
    return response


@main.route('/api/users/post', methods=['POST'])
def update_user():
    # FIXME:
    user_data = user_schema.load(request.json, session=db_session)
    
    try:
        db_session.add(user_data)
        db_session.commit()
        return jsonify('Added')
    except:
        db_session.rollback()
        return 'Error in the db'


@main.route('/api/users/post', methods=['POST'])
def update_user():
    # FIXME:
    brocat_data = brocat_schema.load(request.json, session=db_session)

    try:
        db_session.add(brocat_data)
        db_session.commit()
        return jsonify('Added')
    except:
        db_session.rollback()
        return 'Error in the db'


@main.route('/api/users/<int:id>', methods=['DELETE'])
def delelte_user(id):
    try:
        Users.query.filter_by(id=id).delete()
        db_session.commit()
        return jsonify('User deleted!')
    except:
        db_session.rollback()
        return 'Err in the db'


@main.route('/api/brocats/<int:id>', methods=['DELETE'])
def delete_brocat(id):
    try:
        Brocats.query.filter_by(id=id).delete()
        db_session.commit()
        return jsonify('Brocat deleted!')
    except:
        db_session.rollback()
        return 'Err in the db'






@main.errorhandler(404)
def error(e):
    return f'<h1>{e}</h1> \
            <div><h2>This is a pretty custom message if the template is not found, \
            the famous 404 error</h2></div>'
