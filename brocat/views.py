from flask import render_template, request, session, redirect, url_for
from bcrypt import checkpw

from brocat import app
from brocat.database import db_session
from brocat.models import Users

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.json['email']
        user = request.json['username']
        psw = request.json['password']

        if Users.query.filter_by(username=user).first():
            return 'This user already exists'
        if Users.query.filter_by(e_mail=email).first():
            return 'This email already exsts'

        new_user = Users(user, email, psw)

        try:
            db_session.add(new_user)
            db_session.commit()
            return redirect(url_for('login'))
        except:
            db_session.rollback()
            return 'Error'

    return 'This is the create account page'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.json['username']
        psw = request.json['password']

        user_exists = Users.query.filter_by(username=user).first()
        if user_exists:
            if checkpw(psw.encode('UTF-8'), user_exists.password):
                session['user'] = user
                return redirect(url_for('index'))
            else:
                return 'Invalid password'
        else:
            return 'Username doesn\'t exist'

    return 'This is the login page'


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))