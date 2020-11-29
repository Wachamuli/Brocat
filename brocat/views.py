from flask import render_template, request, session, redirect, url_for, \
    flash

from brocat.database import db_session
from brocat import app
from brocat.models import Users


@app.route('/')
def index():
    if 'user' in session:
        user = session['user']
        # Provisional
        return render_template('index.html', user=user)
    return render_template('index.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        if not 'user' in session:
            email = request.json['email']
            user = request.json['username']
            psw = request.json['password']

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
                return 'Error'

        else:
            return redirect(url_for('index'))

    return 'This is the create account page'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.json['username']
        psw = request.json['password']
        user_exists = Users.query.filter_by(username=user).first()

        if user_exists and user_exists.check_psw(psw):
            session['user'] = user
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password.'

    return 'This is the login page'


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout successfully')
    return redirect(url_for('login'))
