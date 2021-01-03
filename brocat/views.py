import os
import random
import jwt
import datetime
from functools import wraps

from flask import render_template, redirect, flash, request, \
    Blueprint, abort, current_app as app, send_from_directory, \
    jsonify, make_response
from flask_login import login_user, logout_user, login_required, \
    current_user
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin
from jinja2 import TemplateNotFound

from brocat.database import db_session
from brocat.models import User, Brocat, users_schema, brocats_schema, \
    user_schema, brocat_schema
from brocat.forms import CreateAccountForm, LoginForm, UploadBrocatForm

main = Blueprint('main', __name__)


def _render_template(template, **context):
    try:
        return render_template(template, **context)
    except TemplateNotFound as err:
        abort(404, description=err)


@main.route('/')
def index():
    total_brocats = Brocat.query.count()
    encontered_list = []
    for _ in range(0, 20): # 20 is only a placeholder to total_brocats
        rand = random.randint(1, total_brocats)
        brocat = Brocat.query.filter_by(id=rand).first()
        encontered_list.append(brocat)

    return _render_template('index.html', brocats_list=encontered_list)


@main.route('/watch=<int:brocat_id>')
def watch(brocat_id):
    brocat = Brocat.query.get(brocat_id)
    if brocat:
        return _render_template('watch.html', brocat=brocat)

    return 'No available'


@main.route('/create_account', methods=['GET', 'POST'])
def create_account():
    ca_form = CreateAccountForm()
    if ca_form.validate_on_submit():
        new_user = User(
            ca_form.email.data,
            ca_form.username.data,
            ca_form.password.data
        )

        try:
            db_session.add(new_user)
            db_session.commit()
        except:
            db_session.rollback()
            return 'Error in the db'

        return redirect('/login')

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


@main.route('/home/')
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

        new_brocat = Brocat(
            title,
            thumbnail_filename,
            audio_filename,
            description
        )

        try:
            db_session.add(new_brocat)
            db_session.commit()
        except:
            db_session.rollback()
            return 'Error in the db'

        flash('Uploaded Brocat')
        return redirect('/')

    return _render_template('upload_brocat.html', form=upload_form)


@main.route('/get_aud/<audname>')
def get_aud(audname):
    return send_from_directory(app.config['AUDIOS_FOLDER'], filename=audname)


@main.route('/get_img/<imgname>')
def get_img(imgname):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename=imgname)


# * API

@main.route('/api/auth/login', methods=['POST'])
def login_api():
    if request.json != None:
        username = request.json['username']
        password = request.json['password']
        remember = request.json['remember']
        user_exists = User.query.filter_by(username=username).first()

        if user_exists and user_exists.check_psw(password):
            token = jwt.encode({
                'username': user_exists.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
                app.config['SECRET_KEY']
            )
            login_user(user_exists, remember=remember)

            return jsonify({'token': token.decode('UTF-8')})

        return jsonify({'Invalid username or password'})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic Realm = "login required"'})


@main.route('/api/current_user')
def get_current_user():
    if not current_user:
        return jsonify({'message': 'No user log in yet'})
        
    return jsonify({'current_user': current_user.username})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Missing token'})

        try:
            jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Invalid token'})

        return f(*args, **kwargs)

    return decorated


@main.route('/api/users')
def all_users():
    all_users = User.query.all()
    response = users_schema.dump(all_users)
    if len(response) == 0:
        response = {'message': 'There are no users'}, 404

    return jsonify(response)


@main.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    response = user_schema.dump(user)
    if len(response) == 0:
        response = {'message': 'User not found!'}, 404

    return jsonify(response)


@main.route('/api/brocats')
def all_brocats():
    all_brocats = Brocat.query.all()
    response = brocats_schema.dump(all_brocats)
    if len(response) == 0:
        response = {'message': 'There are no brocats'}, 404

    return jsonify(response)


@main.route('/api/brocats/<int:id>')
def get_brocat(id):
    brocat = Brocat.query.get(id)
    response = brocat_schema.dump(brocat)
    if len(response) == 0:
        response = {'message': 'Brocat not found!'}, 404

    return jsonify(response)


@main.route('/api/users', methods=['POST'])
@token_required
def post_a_user():
    user_data = user_schema.load(request.json, session=db_session)

    try:
        db_session.add(user_data)
        db_session.commit()
    except:
        db_session.rollback()
        return jsonify({'message': 'Error in the db'})

    return jsonify({"message": "Added"})


@main.route('/api/brocats', methods=['POST'])
@token_required
def post_a_brocat():
    brocat_data = brocat_schema.load(request.json, session=db_session)

    try:
        db_session.add(brocat_data)
        db_session.commit()
    except:
        db_session.rollback()
        return jsonify({'message': 'Error in the db'})

    return jsonify({"message": "Added"})


@main.route('/api/users/<int:id>', methods=['PUT'])
@token_required
def patch_user(id):
    user = User.query.get(id)
    if user and user.id == current_user.id:
        data = request.json
        for key in data:
            if key == 'email':
                user.email = data['email']
            if key == 'username':
                user.username = data['username']
            if key == 'password':
                # encode() is not necessary with SQLAlchemy String(convert_unicode=True) and
                # the @staticmethod hash_psw() is not necessary with a property
                user.password = User.hash_psw(data['password'])

        try:
            db_session.commit()
        except:
            return jsonify({'message': 'Error in the db'})

        return jsonify({'message': 'Updated succesfully'})

    return jsonify({'message': 'User not found'}), 404


@main.route('/api/brocats/<int:id>', methods=['PUT'])
@token_required
def patch_brocat(id):
    brocat = Brocat.query.get(id)
    if brocat and brocat.author.id == current_user.id:
        data = request.json
        for key in data:
            if key == 'title':
                brocat.title = data['title']
            if key == 'thumbnail':
                brocat.thumbnail = data['thumbnail']
            if key == 'audio':
                brocat.audio = data['audio']
            if key == 'description':
                brocat.description = data['description']

        try:
            db_session.commit()
        except:
            return jsonify({'message': 'Error in the db'})
        
        return jsonify({'message': 'Updated succesfully!'})

    return jsonify({'message': 'Brocat not found!'}), 404


@main.route('/api/users/<int:id>', methods=['DELETE'])
@token_required
def delete_user(id):
    user_to_del = User.query.filter_by(id=id).first()

    if not(user_to_del and user_to_del.id == current_user.id):
        return jsonify('User not found'), 404

    try:
        db_session.delete(user_to_del)
        db_session.commit()
    except:
        db_session.rollback()
        return jsonify({'message': 'Error in the db'})

    return jsonify({'message': 'User deleted!'})


@main.route('/api/brocats/<int:id>', methods=['DELETE'])
@token_required
def delete_brocat(id):
    brocat_to_del = Brocat.query.filter_by(id=id).first()
    if not(brocat_to_del and brocat_to_del.id in current_user.brocats):
        return jsonify('Brocat not found!'), 404

    try:
        db_session.delete(brocat_to_del)
        db_session.commit()
    except:
        db_session.rollback()
        return jsonify({'message': 'Error in the db'})

    return jsonify({ "message" : "Brocat deleted!" })


@main.errorhandler(404)
def resource_not_found(e):
    return f'<h1>{e}</h1> \
            <div><h2>This is a pretty custom message if the template is not found, \
            the famous 404 error</h2></div>', 404
