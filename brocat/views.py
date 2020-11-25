from flask import render_template, request

from brocat import app
from brocat.database import db_session
from brocat.models import Users
from brocat.forms import CreateAccountForm

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreateAccountForm()
    print(form.username.label)
    if form.validate_on_submit():
        try:
            new_user = Users(
                request.form.get('email'),
                request.form.get('usrname'),
                request.form.get('psw')
            )
        except:
            db_session.add(new_user)
            db_session.commit()
            return 'added'

    return render_template('index.html')